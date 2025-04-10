import datetime
import time
import requests
import os
import sys
import traceback
import hmac
import json
import hashlib
import base64
import copy
import utils

# tracked device and API data
gv_solis_dict = {}
gv_solis_dict['last_updated'] = 0
gv_solis_dict['day_last_updated'] = 0
gv_solis_dict['month_last_updated'] = 0
gv_solis_dict['year_last_updated'] = 0

# day, month and year records
gv_solis_dict['day'] = []
gv_solis_dict['month'] = []
gv_solis_dict['year'] = []
gv_solis_dict['live'] = {}
gv_solis_dict['total'] = {}

gv_solis_dict['total']['import'] = 0
gv_solis_dict['total']['export'] = 0

# timestamps to track the next call
day_ts = 0
month_ts = 0
year_ts = 0

# battery presence tracking
gv_battery_is_present = False

# adapted from code
# in https://github.com/Gentleman1983/ginlong_solis_api_connector
def get_solis_cloud_data(
        config,
        url_part, 
        request) -> dict:
    """
    Calls Solis cloud API to retrieve inverter data. Handles all 
    the complex authentication steps required to generate headers etc

    Args:
    config    - config dict 
    url_part  - API URL function/target appended to base URL
    request   - API request body

    Returns: dict parsed from API JSON response
    """

    # Payload MD5
    payload_str = json.dumps(request)
    md5 = base64.b64encode(
            hashlib.md5(
                payload_str.encode('utf-8')).digest()).decode('utf-8')

    # Authorization header
    now = datetime.datetime.now(
            datetime.timezone.utc).strftime(
                    '%a, %d %b %Y %H:%M:%S GMT')
    encrypt_str = 'POST\n%s\napplication/json\n%s\n%s' % (
            md5,
            now,
            url_part
            )
    hmac_obj = hmac.new(
            config['solis']['key_secret'].encode('utf-8'),
            msg = encrypt_str.encode('utf-8'),
            digestmod = hashlib.sha1,
            )
    authorization = 'API %s:%s' % (
            config['solis']['key_id'],
            base64.b64encode(hmac_obj.digest()).decode('utf-8')
            )
    headers = {
            'Content-MD5': md5,
            'Content-Type': 'application/json',
            'Date': now,
            'Authorization': authorization,
            }
    target_url = config['solis']['api_host'] + url_part
    utils.log_message(
            utils.gv_verbose,
            'API: \nURL:%s \nHeaders:%s \nrequest:\n%s\n' % (
                target_url,
                json.dumps(headers, indent = 4),
                json.dumps(request, indent = 4)
                )
            )

    try:
        resp = requests.post(
                target_url,
                headers = headers,
                timeout = 20,
                json = request)

        if resp.status_code == 200:
            utils.log_message(
                    utils.gv_verbose,
                    'Response:\n%s\n' % (
                        json.dumps(resp.json(), indent = 4)
                        )
                    )
            return resp.json()
        else:
            utils.log_message(
                    1,
                    'Solis API Failure.. URL:%s status:%d text:\n%s' % (
                        target_url,
                        resp.status_code,
                        resp.text) 
                    )
            return None

    # exceptions
    except requests.exceptions.Timeout:
        utils.log_message(
                1,
                'Solis API timeout.. URL:%s' % (target_url) 
                )

    except Exception as ex:
        utils.log_message(
                1,
                'Solis API exception.. URL:%s' % (target_url) 
                )

        # exception details
        for tb_line in traceback.format_exception(ex.__class__, ex, ex.__traceback__):
            utils.log_message(1, tb_line.strip('\n'))

    return None


def get_inverter_day_data(config):
    """
    Gets inverter data for the last 36 hours

    Args:
    config    - gloval config
    """
    global day_ts
    global gv_solis_dict
    global gv_battery_is_present

    now = int(time.time())
    # do not refresh before time
    if now < day_ts:
        return

    utils.log_message(
            1,
            "Updating Solis Day Data"
            )

    # objective is the last 36 hours of data
    # with relative solar kWh per hour.
    # solis gives multiple records per hour
    # with acumulated kWh and snapshot kw values
    #
    # So... there's a bit of work to get this in shape:
    # * get all solis records for today and yesterday
    # * scan solis records and reduce to one per hour with largest kWh value
    # * scan records and adjust accumulated kWh to relative kWh per hour
    # * fill in missing hours with zero solar generation records
    # * cull list to 36 hours up to last hour as reported by solis

    # 36 hour back-reference period could be spanning 2-3 days
    # so we offset by 36 hours and pull each day spanned
    dt_now = datetime.datetime.now()
    start_dt = dt_now - datetime.timedelta(hours = 36)
    start_day = start_dt.date()
    end_day = dt_now.date()

    data_dict = {}
    solis_snap_list = []

    request = {}
    request['sn'] = config['solis']['inverter_sn']
    request['TimeZone'] = 0

    while start_day <= end_day:
        request['time'] = start_day.strftime('%Y-%m-%d')
        day_dict = get_solis_cloud_data(
                config,
                '/v1/api/inverterDay', 
                request)
        if not day_dict:
            return 

        # append to list and increment day
        solis_snap_list += day_dict['data']
        start_day = start_day + datetime.timedelta(days = 1)

        # delay between calls
        time.sleep(2)

    for solis_snap_rec in solis_snap_list:
        # battery detection
        # can flick on and off depending on system
        # issues.. so we scan all data first and turn it 
        # on when first encountered
        if solis_snap_rec['batteryType'] != 0:
            gv_battery_is_present = True

    for solis_snap_rec in solis_snap_list:
        ts = int(solis_snap_rec['dataTimestamp']) // 1000
        ts_dt = datetime.datetime.fromtimestamp(ts)

        # unique key for hour
        key = '%04d-%02d-%02d-%02d' % (
                ts_dt.year,
                ts_dt.month,
                ts_dt.day,
                ts_dt.hour)
        if key in data_dict:
            # retrieve existing
            usage_rec = data_dict[key]
        else:
            # init and index new record
            usage_rec = {}
            usage_rec['key'] = key
            usage_rec['year'] = ts_dt.strftime('%Y')
            usage_rec['month'] = ts_dt.strftime('%b')
            usage_rec['day'] = ts_dt.day
            usage_rec['hour'] = ts_dt.hour
            usage_rec['solar'] = 0
            usage_rec['import'] = 0
            usage_rec['export'] = 0
            usage_rec['consumed'] = 0
            usage_rec['solar_consumed'] = 0

            if gv_battery_is_present:
                usage_rec['battery_charge'] = 0
                usage_rec['battery_discharge'] = 0

            data_dict[key] = usage_rec

        # overwrite acumulated solar generation 
        # to date with max value
        usage_rec['solar'] = max(usage_rec['solar'], solis_snap_rec['eToday'])
        # FIXME it seems on 3ph API data, both gridPurchasedTodayEnergy and gridSellTodayEnergy are reported as Wh
        # as they seem to be much higher. In fact gridSellTodayEnergy might be x100 versus gridPurchasedTodayEnergy x1000
        # observed on goofy values on pgannon site but also showing on cloud website
        usage_rec['import'] = max(usage_rec['import'], solis_snap_rec['gridPurchasedTodayEnergy'])
        usage_rec['export'] = max(usage_rec['export'], solis_snap_rec['gridSellTodayEnergy'])
        usage_rec['consumed'] = max(usage_rec['consumed'], solis_snap_rec['homeLoadTodayEnergy'])
        if gv_battery_is_present:
            usage_rec['battery_charge'] = max(usage_rec['battery_charge'], solis_snap_rec['batteryTodayChargeEnergy'])
            usage_rec['battery_discharge'] = max(usage_rec['battery_discharge'], solis_snap_rec['batteryTodayDischargeEnergy'])

    # adjust values to relative 
    # difference from previous hours record
    # offset scope is for given day only
    field_list = [
            'solar',
            'import',
            'export',
            'consumed',
            'battery_charge',
            'battery_discharge',
            ]
    offset_dict = {}
    for field in field_list:
        offset_dict[field] = {}

    for key in sorted(data_dict.keys()):
        usage_rec = data_dict[key]

        for field in field_list:

            # not all fields present 
            # such as battery props
            if not field in usage_rec:
                continue

            # offset keyed per unique day
            # init offset to 0 for first
            # encounter of given day
            offset_key = usage_rec['day']
            if not offset_key in offset_dict[field]:
                offset_dict[field][offset_key] = 0

            # adjust accumulated solar to relative
            usage_rec[field] = usage_rec[field] - offset_dict[field][offset_key]

            # negative protection
            if usage_rec[field] < 0:
                usage_rec[field] = 0

            # add relative value to offset for next hour
            offset_dict[field][offset_key] += usage_rec[field]

        # calculate the solar consumed from the adjusted numbers
        usage_rec['solar_consumed'] = max(0, usage_rec['solar'] - usage_rec['export'])
        if usage_rec['solar_consumed'] < 0:
            usage_rec['solar_consumed'] = 0

        # environmental calculations
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

    # cull to last 36 hours
    sorted_keys = sorted(data_dict.keys())[-36:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    data_list = []
    for key in sorted(culled_dict.keys()):
        data_list.append(culled_dict[key])

    gv_solis_dict['day'] = data_list

    latest_snap_rec = solis_snap_list[-1]
    gv_solis_dict['last_updated'] = int(latest_snap_rec['dataTimestamp']) // 1000
    gv_solis_dict['day_last_updated'] = int(time.time())

    solar = latest_snap_rec['pac'] / 1000
    grid = latest_snap_rec['pSum'] / 1000 
    consumed = latest_snap_rec['familyLoadPower'] / 1000 
    battery = latest_snap_rec['batteryPower'] / 1000
    battery_soc = latest_snap_rec['batteryCapacitySoc']

    # for solar, zero readings below 10W
    if solar <= 0.010:
        solar = 0

    live_rec = gv_solis_dict['live']
    live_rec['ts'] = gv_solis_dict['last_updated']

    # broken out values for local time
    live_dt = datetime.datetime.fromtimestamp(live_rec['ts'])
    live_rec['year'] = '%04d' %(
                        live_dt.year)
    live_rec['month'] = live_dt.strftime('%b')
    live_rec['day'] = live_dt.day
    live_rec['hour'] = live_dt.hour
    live_rec['minute'] = live_dt.minute
    live_rec['second'] = live_dt.second

    if grid < 0:
        # negative => exporting
        live_rec['export'] = grid * -1
        live_rec['import'] = 0
    else:
        # positive => importing
        live_rec['export'] = 0
        live_rec['import'] = grid 

    live_rec['solar'] = solar

    if gv_battery_is_present:
        # populate charge and one of charge or discharge
        # purge charge and discharge initially
        for field in ['battery_discharge', 'battery_charge']:
            if field in live_rec:
                del live_rec[field]

            live_rec['battery_soc'] = battery_soc

        if battery >= 0:
            live_rec['battery_charge'] = battery
        else:
            live_rec['battery_discharge'] = battery * -1

    live_rec['solar_consumed'] = 0
    if live_rec['solar'] > 0:
        live_rec['solar_consumed'] = max(0, live_rec['solar'] - live_rec['export'])

    live_rec['consumed'] = consumed

    live_rec['co2'] = (config['environment']['gco2_kwh'] * solar) / 1000
    live_rec['trees'] = config['environment']['trees_kwh'] * solar

    # total accumulated values for import, export and solar
    total_rec = gv_solis_dict['total']
    latest_snap_rec = solis_snap_list[-1]
    total_rec['import'] = latest_snap_rec['gridPurchasedTotalEnergy']
    total_rec['export'] = latest_snap_rec['gridSellTotalEnergy']
    total_rec['solar'] = latest_snap_rec['eTotal']
    total_rec['consumed'] = latest_snap_rec['homeLoadTotalEnergy']
    if gv_battery_is_present:
        usage_rec['battery_charge'] = solis_snap_rec['batteryTotalChargeEnergy']
        usage_rec['battery_discharge'] = solis_snap_rec['batteryTotalDischargeEnergy']

    total_rec['solar_consumed'] = max(0, total_rec['solar'] - total_rec['export'])
    total_rec['consumed'] = total_rec['solar_consumed'] + total_rec['import']

    total_rec['co2'] = (config['environment']['gco2_kwh'] * total_rec['solar']) / 1000
    total_rec['trees'] = config['environment']['trees_kwh'] * total_rec['solar']

    # new refresh time
    # 5 mins, 20 secs after last official inverter update
    day_ts = gv_solis_dict['last_updated'] + 300 + 20

    return


def get_inverter_month_data(config):
    """
    Gets inverter data for the last 30 days

    Args:
    config    - gloval config
    """
    global month_ts
    global day_ts
    global gv_solis_dict
    global gv_battery_is_present

    now = int(time.time())
    dt_now = datetime.datetime.today() 

    # do not refresh before time
    if now < month_ts:
        return

    utils.log_message(
            1,
            "Updating Solis Month Data"
            )

    # get a reference data 30 days back
    # to determine first month to query
    now_dt = datetime.datetime.now()
    start_dt = now_dt - datetime.timedelta(days = 30)
    start_month = start_dt.date()
    end_month = now_dt.date()
    # offset day to late in the month
    end_month = end_month.replace(day = 28)

    data_dict = {}
    solis_day_list = []

    request = {}
    request['sn'] = config['solis']['inverter_sn']
    request['TimeZone'] = 0

    while start_month <= end_month:
        request['month'] = start_month.strftime('%Y-%m')

        # get month
        month_dict = get_solis_cloud_data(
                config,
                '/v1/api/inverterMonth', 
                request)
        if not month_dict:
            return 

        # append to list and increment month
        # timedelta does not suport 
        solis_day_list += month_dict['data']

        # transition to next month
        # force day to earliest last day of any month
        # add 5 days and will transition a month
        # timedelta lacks a months option, hence this hack
        # the jump from 28+5 will also be less than the 28 we asserted
        # on the end_month above. this is for the while condition of
        # the loop
        start_month = start_month.replace(day = 28)
        start_month = start_month + datetime.timedelta(days = 5)

        # delay between calls
        time.sleep(2)

    for solis_day_rec in solis_day_list:
        ts = solis_day_rec['date'] // 1000
        ts_dt = datetime.datetime.fromtimestamp(ts)
        key = '%04d-%02d-%02d-00' % (
                ts_dt.year,
                ts_dt.month,
                ts_dt.day)
        usage_rec = {}
        usage_rec['key'] = key
        usage_rec['import'] = solis_day_rec['gridPurchasedEnergy']
        usage_rec['export'] = solis_day_rec['gridSellEnergy']
        usage_rec['solar'] = solis_day_rec['energy']
        usage_rec['consumed'] = solis_day_rec['consumeEnergy']
        if gv_battery_is_present:
            usage_rec['battery_charge'] = solis_day_rec['batteryChargeEnergy']
            usage_rec['battery_discharge'] = solis_day_rec['batteryDischargeEnergy']

        usage_rec['solar_consumed'] = max(0, usage_rec['solar'] - usage_rec['export'])
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')
        usage_rec['day'] = ts_dt.day

        # environmental calculations
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

        data_dict[ts] = usage_rec

    # cull to last 30 days
    sorted_keys = sorted(data_dict.keys())[-30:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    month_data = []
    for key in sorted(culled_dict.keys()):
        month_data.append(culled_dict[key])

    gv_solis_dict['month'] = month_data
    gv_solis_dict['month_last_updated'] = int(time.time())

    # get month data 20 seconds after the day update
    # ensures the "today" record updates quickly
    month_ts = day_ts + 20

    return 


def get_inverter_year_data(config):
    """
    Gets inverter data for the last 12 months

    Args:
    config    - gloval config
    """
    global year_ts
    global gv_solis_dict
    global gv_battery_is_present

    now = int(time.time())
    dt_now = datetime.datetime.today() 

    # do not refresh before time
    if now < year_ts:
        return

    utils.log_message(
            1,
            "Updating Solis Year Data"
            )

    today = datetime.date.today()
    data_dict = {}

    # we want last 12 months
    # but have to get 2 years of data
    # and cull
    solis_month_list = []

    request = {}
    request['sn'] = config['solis']['inverter_sn']
    request['TimeZone'] = 0

    # last year
    request['year'] = '%d' % (today.year - 1)
    year_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterYear', 
            request)
    if not year_dict:
        return None
    solis_month_list += year_dict['data']

    # delay between calls
    time.sleep(2)

    # this year
    request['year'] = '%d' % (today.year)
    year_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterYear', 
            request)
    if not year_dict:
        return None
    solis_month_list += year_dict['data']

    for solis_month_rec in solis_month_list:
        ts = solis_month_rec['date'] // 1000
        ts_dt = datetime.datetime.fromtimestamp(ts)
        key = '%04d-%02d-01-00' % (
                ts_dt.year,
                ts_dt.month)
        usage_rec = {}
        usage_rec['key'] = key
        usage_rec['import'] = solis_month_rec['gridPurchasedEnergy']
        usage_rec['export'] = solis_month_rec['gridSellEnergy']
        usage_rec['solar'] = solis_month_rec['energy']
        usage_rec['consumed'] = solis_month_rec['consumeEnergy']
        if gv_battery_is_present:
            usage_rec['battery_charge'] = solis_month_rec['batteryChargeEnergy']
            usage_rec['battery_discharge'] = solis_month_rec['batteryDischargeEnergy']

        usage_rec['solar_consumed'] = max(0, usage_rec['solar'] - usage_rec['export'])
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')

        # environmental calculations
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

        data_dict[ts] = usage_rec

    # cull to last 12 months
    sorted_keys = sorted(data_dict.keys())[-12:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    year_data = []
    for key in sorted(culled_dict.keys()):
        year_data.append(culled_dict[key])

    gv_solis_dict['year'] = year_data
    gv_solis_dict['year_last_updated'] = int(time.time())

    # new refresh time
    # 15 mins from now
    year_ts = now + (60 * 15)

    return 


def get_data(config):
    """
    Gets inverter data. This is the module common function 
    called by the parent solar_monnitor.py script. It manages 
    all lower level calls for day, month and year and returns the 
    results in a common format dict object

    Args:
    config    - gloval config

    Returns: tuple of the data dict and refresh interval 
             (derived from next predicted update time)
    """
    global gv_solis_dict
    global day_ts

    utils.log_message(
            1,
            "Checking Solis Cloud Data.. timestamps: day:%s month:%s year:%s" % (
                day_ts,
                month_ts,
                year_ts
                )
            )
    get_inverter_day_data(config)
    get_inverter_month_data(config)
    get_inverter_year_data(config)

    # update interval based on next day_ts
    # minus now
    # check for <= 0 to indicate API failure 
    # and default to a 30-second update
    if day_ts <= 0:
        update_interval = 30
    else:
        now = int(time.time())
        update_interval = day_ts - now

    # negative scenarios
    # fall back to 5-min refresh
    # This will happen as the string inverter stops 
    # updating
    if update_interval < 0:
        update_interval = 300
        day_ts = now + update_interval

    utils.log_message(
            utils.gv_verbose,
            'Solis Data Dict:\n%s' % (
                json.dumps(
                    gv_solis_dict, 
                    indent = 4)
                ) 
            )

    # return dep copy of data
    # and a the derived refresh interval
    return copy.deepcopy(gv_solis_dict), update_interval
