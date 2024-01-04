import datetime
import time
import requests
import os
import sys
import hmac
import json
import hashlib
import base64
import utils

# tracked device and API data
gv_data_dict = {}
gv_data_dict['last_updated'] = 0

# day, month and year records
gv_data_dict['day'] = []
gv_data_dict['month'] = []
gv_data_dict['year'] = []

# metrics
gv_data_dict['metrics'] = {}
gv_data_dict['metrics']['live'] = {}
gv_data_dict['metrics']['live']['import'] = 0
gv_data_dict['metrics']['live']['solar'] = 0
gv_data_dict['metrics']['live']['solar_consumed'] = 0
gv_data_dict['metrics']['live']['export'] = 0
gv_data_dict['metrics']['live']['consumed'] = 0

gv_data_dict['metrics']['today'] = {}
gv_data_dict['metrics']['today']['title'] = 'Today'
gv_data_dict['metrics']['today']['import'] = 0
gv_data_dict['metrics']['today']['solar'] = 0
gv_data_dict['metrics']['today']['solar_consumed'] = 0
gv_data_dict['metrics']['today']['export'] = 0
gv_data_dict['metrics']['today']['consumed'] = 0

gv_data_dict['metrics']['yesterday'] = {}
gv_data_dict['metrics']['yesterday']['title'] = 'Yesterday'
gv_data_dict['metrics']['yesterday']['import'] = 0
gv_data_dict['metrics']['yesterday']['solar'] = 0
gv_data_dict['metrics']['yesterday']['solar_consumed'] = 0
gv_data_dict['metrics']['yesterday']['export'] = 0
gv_data_dict['metrics']['yesterday']['consumed'] = 0

gv_data_dict['metrics']['this_month'] = {}
gv_data_dict['metrics']['this_month']['title'] = 'This Month'
gv_data_dict['metrics']['this_month']['import'] = 0
gv_data_dict['metrics']['this_month']['solar'] = 0
gv_data_dict['metrics']['this_month']['solar_consumed'] = 0
gv_data_dict['metrics']['this_month']['export'] = 0
gv_data_dict['metrics']['this_month']['consumed'] = 0

gv_data_dict['metrics']['last_month'] = {}
gv_data_dict['metrics']['last_month']['title'] = 'Last Month'
gv_data_dict['metrics']['last_month']['import'] = 0
gv_data_dict['metrics']['last_month']['solar'] = 0
gv_data_dict['metrics']['last_month']['solar_consumed'] = 0
gv_data_dict['metrics']['last_month']['export'] = 0
gv_data_dict['metrics']['last_month']['consumed'] = 0

gv_data_dict['metrics']['last_12_months'] = {}
gv_data_dict['metrics']['last_12_months']['title'] = 'Last 12 Months'
gv_data_dict['metrics']['last_12_months']['import'] = 0
gv_data_dict['metrics']['last_12_months']['solar'] = 0
gv_data_dict['metrics']['last_12_months']['solar_consumed'] = 0
gv_data_dict['metrics']['last_12_months']['export'] = 0
gv_data_dict['metrics']['last_12_months']['consumed'] = 0

# timestamps to track the next call
month_ts = 0
year_ts = 0

# adapted from code
# in https://github.com/Gentleman1983/ginlong_solis_api_connector
def get_solis_cloud_data(
        config,
        url_part, 
        request) -> dict:

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
    utils.log_message(
            utils.gv_verbose,
            'API: \nURL:%s \nHeaders:%s \nrequest:\n%s\n' % (
                config['solis']['api_host'] + url_part,
                json.dumps(headers, indent = 4),
                json.dumps(request, indent = 4)
                )
            )
    try:
        resp = requests.post(
                config['solis']['api_host'] + url_part,
                headers = headers,
                json = request)
        utils.log_message(
                utils.gv_verbose,
                'Response:\n%s\n' % (
                    json.dumps(resp.json(), indent = 4)
                    )
                )

        return resp.json()
    except:
        utils.log_message(
                1,
                'Solis API failure.. URL:%s' % (config['solis']['api_host'] + url_part) 
                )
        return None


def get_inverter_day_data(config):
    global gv_data_dict

    utils.log_message(
            1,
            "Updating Solis Day Data"
            )

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days = 1)

    data_dict = {}

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

    solis_snap_list = []

    request = {}
    request['sn'] = config['solis']['inverter_sn']
    request['TimeZone'] = 0

    # yesterday
    request['time'] = yesterday.strftime('%Y-%m-%d')
    day_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterDay', 
            request)
    if not day_dict:
        return 

    solis_snap_list += day_dict['data']

    # delay between calls
    time.sleep(2)

    # today
    request['time'] = today.strftime('%Y-%m-%d')
    day_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterDay', 
            request)
    if not day_dict:
        return 

    solis_snap_list += day_dict['data']

    for solis_snap_rec in solis_snap_list:
        ts = int(solis_snap_rec['dataTimestamp']) // 1000
        ts_dt = datetime.datetime.fromtimestamp(ts)

        # key day-hour
        key = ts_dt.strftime('%d-%H')
        if key in data_dict:
            # retrieve existing
            usage_rec = data_dict[key]
        else:
            # init and index new record
            usage_rec = {}
            usage_rec['year'] = ts_dt.strftime('%Y')
            usage_rec['month'] = ts_dt.strftime('%b')
            usage_rec['day'] = ts_dt.day
            usage_rec['hour'] = ts_dt.hour
            usage_rec['solar'] = 0
            usage_rec['import'] = 0
            usage_rec['export'] = 0
            usage_rec['consumed'] = 0
            usage_rec['solar_consumed'] = 0

            data_dict[key] = usage_rec

        # overwrite acumulated solar generation 
        # to date with max value
        usage_rec['solar'] = max(usage_rec['solar'], solis_snap_rec['eToday'])
        usage_rec['import'] = max(usage_rec['import'], solis_snap_rec['gridPurchasedTodayEnergy'])
        usage_rec['export'] = max(usage_rec['export'], solis_snap_rec['gridSellTodayEnergy'])
        usage_rec['consumed'] = max(usage_rec['consumed'], solis_snap_rec['homeLoadTodayEnergy'])
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']

    # adjust values to relative 
    # difference from previous hours record
    # offset scope is for given day only
    field_list = [
            'solar',
            'import',
            'export',
            'consumed',
            'solar_consumed',
            ]
    offset_dict = {}
    for field in field_list:
        offset_dict[field] = {}

    for key in sorted(data_dict.keys()):
        usage_rec = data_dict[key]

        for field in field_list:
            # offset keyed per unique day
            # init offset to 0 for first
            # encounter of given day
            offset_key = usage_rec['day']
            if not offset_key in offset_dict[field]:
                offset_dict[field][offset_key] = 0

            # adjust accumulated solar to relative
            usage_rec[field] = usage_rec[field] - offset_dict[field][offset_key]

            # add relative value to offset for next hour
            offset_dict[field][offset_key] += usage_rec[field]

        # re-calculate the solar consumed from the adjusted numbers
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']

        # environmental metrics
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

    # fill in empty records for absent hours
    # but not beyond the latest record
    latest_key = sorted(data_dict.keys())[-1]
    last_day = data_dict[latest_key]['day']
    last_hour = data_dict[latest_key]['hour']

    for dt in [yesterday, today]:
        for hour in range(0, 24):
            key = '%02d-%02d' % (
                    dt.day,
                    hour)

            if dt.day == last_day and hour > last_hour:
                break

            if not key in data_dict:
                usage_rec = {}
                data_dict[key] = usage_rec
                usage_rec['year'] = dt.strftime('%Y')
                usage_rec['month'] = dt.strftime('%b')
                usage_rec['day'] = dt.day
                usage_rec['hour'] = hour
                usage_rec['solar'] = 0
                usage_rec['import'] = 0
                usage_rec['export'] = 0
                usage_rec['consumed'] = usage_rec['import']
                usage_rec['solar_consumed'] = 0
                usage_rec['co2'] = 0
                usage_rec['trees'] = 0

    # cull to last 36 hours
    sorted_keys = sorted(data_dict.keys())[-36:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    data_list = []
    for key in sorted(culled_dict.keys()):
        data_list.append(culled_dict[key])

    gv_data_dict['day'] = data_list

    latest_snap_rec = solis_snap_list[-1]
    solar = latest_snap_rec['pac'] / 1000
    grid = latest_snap_rec['pSum'] / 1000

    if grid >= 0:
        gv_data_dict['metrics']['live']['import'] = grid
        gv_data_dict['metrics']['live']['export'] = 0
    else:
        gv_data_dict['metrics']['live']['import'] = 0
        gv_data_dict['metrics']['live']['export'] = grid * -1

    gv_data_dict['metrics']['live']['solar'] = solar

    gv_data_dict['metrics']['live']['solar_consumed'] = gv_data_dict['metrics']['live']['solar'] - gv_data_dict['metrics']['live']['export']
    gv_data_dict['metrics']['live']['consumed'] = gv_data_dict['metrics']['live']['import'] + gv_data_dict['metrics']['live']['solar_consumed'] 

    gv_data_dict['last_updated'] = int(latest_snap_rec['dataTimestamp']) // 1000

    return


def get_inverter_month_data(config):
    global month_ts
    global gv_data_dict

    now = int(time.time())
    dt_now = datetime.datetime.today() 

    # do not refresh before time
    if now < month_ts:
        return

    utils.log_message(
            1,
            "Updating Solis Month Data"
            )

    dt_today = datetime.date.today()
    dt_yesterday = dt_today - datetime.timedelta(days = 1)
    dt_last_month = dt_today.replace(day = 1) - datetime.timedelta(days = 1)

    data_dict = {}

    # get 30 days of data
    # will need to request 2 months and cull
    solis_day_list = []

    request = {}
    request['sn'] = config['solis']['inverter_sn']
    request['TimeZone'] = 0

    # last month
    request['month'] = dt_last_month.strftime('%Y-%m')
    month_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterMonth', 
            request)
    if not month_dict:
        return 

    solis_day_list += month_dict['data']

    # delay between calls
    time.sleep(2)

    # this month
    request['month'] = dt_today.strftime('%Y-%m')
    month_dict = get_solis_cloud_data(
            config,
            '/v1/api/inverterMonth', 
            request)
    if not month_dict:
        return 

    solis_day_list += month_dict['data']

    for solis_day_rec in solis_day_list:
        usage_rec = {}
        usage_rec['ts'] = solis_day_rec['date'] // 1000
        ts_dt = datetime.datetime.fromtimestamp(usage_rec['ts'])
        usage_rec['import'] = solis_day_rec['gridPurchasedEnergy']
        usage_rec['export'] = solis_day_rec['gridSellEnergy']
        usage_rec['solar'] = solis_day_rec['energy']

        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')
        usage_rec['day'] = ts_dt.day

        # environmental metrics
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

        data_dict[usage_rec['ts']] = usage_rec

    # cull to last 30 days
    sorted_keys = sorted(data_dict.keys())[-30:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    month_data = []
    for key in sorted(culled_dict.keys()):
        month_data.append(culled_dict[key])

    gv_data_dict['month'] = month_data

    # take todays totals from last recorded day in month
    today_rec = month_data[-1]
    gv_data_dict['metrics']['today']['title'] = 'Today (%s %d %s)' % (
            today_rec['month'], 
            today_rec['day'], 
            today_rec['year'])
    gv_data_dict['metrics']['today']['import'] = today_rec['import']
    gv_data_dict['metrics']['today']['solar'] = today_rec['solar']
    gv_data_dict['metrics']['today']['solar_consumed'] = today_rec['solar_consumed']
    gv_data_dict['metrics']['today']['export'] = today_rec['export']
    gv_data_dict['metrics']['today']['consumed'] = today_rec['import'] +  today_rec['solar_consumed']
    gv_data_dict['metrics']['today']['co2'] = today_rec['co2']
    gv_data_dict['metrics']['today']['trees'] = today_rec['trees']

    if len(month_data) >= 2:
        yesterday_rec = month_data[-2]
        gv_data_dict['metrics']['yesterday']['title'] = 'Yesterday (%s %d %s)' % (
                yesterday_rec['month'], 
                yesterday_rec['day'], 
                yesterday_rec['year'])
        gv_data_dict['metrics']['yesterday']['import'] = yesterday_rec['import']
        gv_data_dict['metrics']['yesterday']['solar'] = yesterday_rec['solar']
        gv_data_dict['metrics']['yesterday']['solar_consumed'] = yesterday_rec['solar_consumed']
        gv_data_dict['metrics']['yesterday']['export'] = yesterday_rec['export']
        gv_data_dict['metrics']['yesterday']['consumed'] = yesterday_rec['import'] + yesterday_rec['solar_consumed']
        gv_data_dict['metrics']['yesterday']['co2'] = yesterday_rec['co2']
        gv_data_dict['metrics']['yesterday']['trees'] = yesterday_rec['trees']

    # new refresh time
    month_ts = ((70 - dt_now.minute) * 60) + now

    # temp hack to refresh every 5 minutes
    #month_ts = now + 280
    return 


def get_inverter_year_data(config):
    global year_ts
    global gv_data_dict

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
        usage_rec = {}
        usage_rec['ts'] = solis_month_rec['date'] // 1000
        ts_dt = datetime.datetime.fromtimestamp(usage_rec['ts'])
        usage_rec['import'] = solis_month_rec['gridPurchasedEnergy']
        usage_rec['export'] = solis_month_rec['gridSellEnergy']
        usage_rec['solar'] = solis_month_rec['energy']

        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')

        # environmental metrics
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

        data_dict[usage_rec['ts']] = usage_rec

    # cull to last 12 months
    sorted_keys = sorted(data_dict.keys())[-12:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    year_data = []
    for key in sorted(culled_dict.keys()):
        year_data.append(culled_dict[key])

    gv_data_dict['year'] = year_data

    # take months totals from last recorded month in year
    month_rec = year_data[-1]
    gv_data_dict['metrics']['this_month']['title'] = 'This Month (%s %s)' % (month_rec['month'], month_rec['year'])
    gv_data_dict['metrics']['this_month']['import'] = month_rec['import']
    gv_data_dict['metrics']['this_month']['solar'] = month_rec['solar']
    gv_data_dict['metrics']['this_month']['solar_consumed'] = month_rec['solar_consumed']
    gv_data_dict['metrics']['this_month']['export'] = month_rec['export']
    gv_data_dict['metrics']['this_month']['consumed'] = month_rec['import'] + month_rec['solar_consumed']
    gv_data_dict['metrics']['this_month']['co2'] = month_rec['co2']
    gv_data_dict['metrics']['this_month']['trees'] = month_rec['trees']

    if len(year_data) >= 2:
        last_month_rec = year_data[-2]
        gv_data_dict['metrics']['last_month']['title'] = 'Last Month (%s %s)' % (last_month_rec['month'], last_month_rec['year'])
        gv_data_dict['metrics']['last_month']['import'] = last_month_rec['import']
        gv_data_dict['metrics']['last_month']['solar'] = last_month_rec['solar']
        gv_data_dict['metrics']['last_month']['solar_consumed'] = last_month_rec['solar_consumed']
        gv_data_dict['metrics']['last_month']['export'] = last_month_rec['export']
        gv_data_dict['metrics']['last_month']['consumed'] = last_month_rec['import'] + last_month_rec['solar_consumed']
        gv_data_dict['metrics']['last_month']['co2'] = last_month_rec['co2']
        gv_data_dict['metrics']['last_month']['trees'] = last_month_rec['trees']

    # last 12 months year
    # add all month records 

    # reset
    gv_data_dict['metrics']['last_12_months']['title'] = 'Last %d Months' % (len(year_data))
    gv_data_dict['metrics']['last_12_months']['import'] = 0
    gv_data_dict['metrics']['last_12_months']['solar'] = 0
    gv_data_dict['metrics']['last_12_months']['solar_consumed'] = 0
    gv_data_dict['metrics']['last_12_months']['export'] = 0
    gv_data_dict['metrics']['last_12_months']['consumed'] = 0
    gv_data_dict['metrics']['last_12_months']['co2'] = 0
    gv_data_dict['metrics']['last_12_months']['trees'] = 0

    for month_rec in year_data:
        gv_data_dict['metrics']['last_12_months']['import'] += month_rec['import']
        gv_data_dict['metrics']['last_12_months']['solar'] += month_rec['solar']
        gv_data_dict['metrics']['last_12_months']['solar_consumed'] += month_rec['solar_consumed']
        gv_data_dict['metrics']['last_12_months']['export'] += month_rec['export']
        gv_data_dict['metrics']['last_12_months']['consumed'] += month_rec['import'] + month_rec['solar_consumed']
        gv_data_dict['metrics']['last_12_months']['co2'] += month_rec['co2']
        gv_data_dict['metrics']['last_12_months']['trees'] += month_rec['trees']

    # new refresh time
    year_ts = ((70 - dt_now.minute) * 60) + now
    return 


def get_data(config):

    global gv_data_dict
    utils.log_message(
            1,
            "Updating Solis Data"
            )

    get_inverter_day_data(config)
    get_inverter_month_data(config)
    get_inverter_year_data(config)

    # update interval based on last_updated
    # time. This gives a form of dynamic tie-in to 
    # the Solis data by assuming the next refresh is ~5 mins after the 
    # last data we had
    now = int(time.time())
    next_update_ts = gv_data_dict['last_updated'] + 300 + 20
    update_interval = next_update_ts - now

    # negative scenarios
    # fall back to 2-min refresh
    if update_interval < 0:
        update_interval = 120

    # return data and fixed sleep of 5 minutes for refresh
    return gv_data_dict, update_interval



