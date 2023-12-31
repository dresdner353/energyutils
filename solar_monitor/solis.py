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
import random

# tracked device and API data
solis_data_dict = {}
solis_data_dict['last_updated'] = 0

# day, month and year records
solis_data_dict['day'] = []
solis_data_dict['month'] = []
solis_data_dict['year'] = []

# metrics
solis_data_dict['metrics'] = {}
solis_data_dict['metrics']['live'] = {}
solis_data_dict['metrics']['live']['import'] = 0
solis_data_dict['metrics']['live']['solar'] = 0
solis_data_dict['metrics']['live']['solar_consumed'] = 0
solis_data_dict['metrics']['live']['export'] = 0
solis_data_dict['metrics']['live']['consumed'] = 0

solis_data_dict['metrics']['today'] = {}
solis_data_dict['metrics']['today']['import'] = 0
solis_data_dict['metrics']['today']['solar'] = 0
solis_data_dict['metrics']['today']['solar_consumed'] = 0
solis_data_dict['metrics']['today']['export'] = 0
solis_data_dict['metrics']['today']['consumed'] = 0

solis_data_dict['metrics']['yesterday'] = {}
solis_data_dict['metrics']['yesterday']['import'] = 0
solis_data_dict['metrics']['yesterday']['solar'] = 0
solis_data_dict['metrics']['yesterday']['solar_consumed'] = 0
solis_data_dict['metrics']['yesterday']['export'] = 0
solis_data_dict['metrics']['yesterday']['consumed'] = 0

solis_data_dict['metrics']['this_month'] = {}
solis_data_dict['metrics']['this_month']['import'] = 0
solis_data_dict['metrics']['this_month']['solar'] = 0
solis_data_dict['metrics']['this_month']['solar_consumed'] = 0
solis_data_dict['metrics']['this_month']['export'] = 0
solis_data_dict['metrics']['this_month']['consumed'] = 0

solis_data_dict['metrics']['last_month'] = {}
solis_data_dict['metrics']['last_month']['import'] = 0
solis_data_dict['metrics']['last_month']['solar'] = 0
solis_data_dict['metrics']['last_month']['solar_consumed'] = 0
solis_data_dict['metrics']['last_month']['export'] = 0
solis_data_dict['metrics']['last_month']['consumed'] = 0

solis_data_dict['metrics']['this_year'] = {}
solis_data_dict['metrics']['this_year']['import'] = 0
solis_data_dict['metrics']['this_year']['solar'] = 0
solis_data_dict['metrics']['this_year']['solar_consumed'] = 0
solis_data_dict['metrics']['this_year']['export'] = 0
solis_data_dict['metrics']['this_year']['consumed'] = 0


# timestamps to track the next call
month_ts = 0
year_ts = 0

# adapted from code
# in https://github.com/Gentleman1983/ginlong_solis_api_connector
def get_solis_cloud_data(
        solis_config,
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
            solis_config['key_secret'].encode('utf-8'),
            msg = encrypt_str.encode('utf-8'),
            digestmod = hashlib.sha1,
            )
    authorization = 'API %s:%s' % (
            solis_config['key_id'],
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
                solis_config['api_host'] + url_part,
                json.dumps(headers, indent = 4),
                json.dumps(request, indent = 4)
                )
            )
    try:
        resp = requests.post(
                solis_config['api_host'] + url_part,
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
                'Solis API failure.. URL:%s' % (solis_config['api_host'] + url_part) 
                )
        return None


def get_inverter_day_data(solis_config):
    global solis_data_dict

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
    request['sn'] = solis_config['inverter_sn']
    request['TimeZone'] = 0

    # yesterday
    request['time'] = yesterday.strftime('%Y-%m-%d')
    day_dict = get_solis_cloud_data(
            solis_config,
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
            solis_config,
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

        # FIXME random import/export
        usage_rec['import'] = random.uniform(0.5, 2)
        usage_rec['export'] = random.uniform(0.0, usage_rec['solar'] * 0.8)
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']

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
                usage_rec['import'] = random.uniform(0.2, 1) # FIXME random
                usage_rec['export'] = 0
                usage_rec['consumed'] = usage_rec['import']
                usage_rec['solar_consumed'] = 0

    # cull to last 36 hours
    sorted_keys = sorted(data_dict.keys())[-36:]
    culled_dict = {}
    for key in sorted_keys:
        culled_dict[key] = data_dict[key]

    # reformat to list of records
    data_list = []
    for key in sorted(culled_dict.keys()):
        data_list.append(culled_dict[key])

    solis_data_dict['day'] = data_list

    latest_snap_rec = solis_snap_list[-1]
    solar = latest_snap_rec['pac'] / 1000
    grid = random.uniform(0, 5)

    if grid >= 0:
        solis_data_dict['metrics']['live']['import'] = grid
        solis_data_dict['metrics']['live']['export'] = 0
    else:
        solis_data_dict['metrics']['live']['import'] = 0
        solis_data_dict['metrics']['live']['export'] = grid * -1

    if solar >= 0.010:
        solis_data_dict['metrics']['live']['solar'] = solar
    else:
        solis_data_dict['metrics']['live']['solar'] = 0

    solis_data_dict['metrics']['live']['solar_consumed'] = solis_data_dict['metrics']['live']['solar'] - solis_data_dict['metrics']['live']['export']
    solis_data_dict['metrics']['live']['consumed'] = solis_data_dict['metrics']['live']['import'] + solis_data_dict['metrics']['live']['solar_consumed'] 

    solis_data_dict['last_updated'] = int(latest_snap_rec['dataTimestamp']) // 1000

    return


def get_inverter_month_data(solis_config):
    global month_ts
    global solis_data_dict

    now = int(time.time())
    dt_now = datetime.datetime.today() 

    # do not refresh before time
    if now < month_ts:
        return

    utils.log_message(
            1,
            "Updating Solis Month Data"
            )

    today = datetime.date.today()
    last_month = today.replace(day = 1) - datetime.timedelta(days = 1)

    data_dict = {}

    # get 30 days of data
    # will need to request 2 months and cull
    solis_day_list = []

    request = {}
    request['sn'] = solis_config['inverter_sn']
    request['TimeZone'] = 0

    # last month
    request['month'] = last_month.strftime('%Y-%m')
    month_dict = get_solis_cloud_data(
            solis_config,
            '/v1/api/inverterMonth', 
            request)
    if not month_dict:
        return 

    solis_day_list += month_dict['data']

    # delay between calls
    time.sleep(2)

    # this month
    request['month'] = today.strftime('%Y-%m')
    month_dict = get_solis_cloud_data(
            solis_config,
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

        # FIXME fakery
        usage_rec['import'] = random.uniform(8, 20)
        usage_rec['export'] = random.uniform(0.0, usage_rec['solar'] * 0.8)

        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')
        usage_rec['day'] = ts_dt.day

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

    solis_data_dict['month'] = month_data

    # take todays totals from last recorded day in month
    today_rec = month_data[-1]
    solis_data_dict['metrics']['today']['import'] = today_rec['import']
    solis_data_dict['metrics']['today']['solar'] = today_rec['solar']
    solis_data_dict['metrics']['today']['solar_consumed'] = today_rec['solar_consumed']
    solis_data_dict['metrics']['today']['export'] = today_rec['export']
    solis_data_dict['metrics']['today']['consumed'] = today_rec['import'] +  today_rec['solar_consumed']

    if len(month_data) >= 2:
        yesterday_rec = month_data[-2]
        solis_data_dict['metrics']['yesterday']['import'] = yesterday_rec['import']
        solis_data_dict['metrics']['yesterday']['solar'] = yesterday_rec['solar']
        solis_data_dict['metrics']['yesterday']['solar_consumed'] = yesterday_rec['solar_consumed']
        solis_data_dict['metrics']['yesterday']['export'] = yesterday_rec['export']
        solis_data_dict['metrics']['yesterday']['consumed'] = yesterday_rec['import'] + yesterday_rec['solar_consumed']

    # new refresh time
    month_ts = ((70 - dt_now.minute) * 60) + now

    # temp hack to refresh every 5 minutes
    #month_ts = now + 280
    return 


def get_inverter_year_data(solis_config):
    global year_ts
    global solis_data_dict

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
    request['sn'] = solis_config['inverter_sn']
    request['TimeZone'] = 0

    # last year
    request['year'] = '%d' % (today.year - 1)
    year_dict = get_solis_cloud_data(
            solis_config,
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
            solis_config,
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

        # FIXME fakery
        usage_rec['import'] = random.uniform(200, 500)
        usage_rec['export'] = random.uniform(50, usage_rec['solar'])

        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']
        usage_rec['year'] = ts_dt.strftime('%Y')
        usage_rec['month'] = ts_dt.strftime('%b')

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

    solis_data_dict['year'] = year_data

    # take months totals from last recorded month in year
    month_rec = year_data[-1]
    solis_data_dict['metrics']['this_month']['import'] = month_rec['import']
    solis_data_dict['metrics']['this_month']['solar'] = month_rec['solar']
    solis_data_dict['metrics']['this_month']['solar_consumed'] = month_rec['solar_consumed']
    solis_data_dict['metrics']['this_month']['export'] = month_rec['export']
    solis_data_dict['metrics']['this_month']['consumed'] = month_rec['import'] + month_rec['solar_consumed']

    if len(year_data) >= 2:
        last_month_rec = year_data[-2]
        solis_data_dict['metrics']['last_month']['import'] = last_month_rec['import']
        solis_data_dict['metrics']['last_month']['solar'] = last_month_rec['solar']
        solis_data_dict['metrics']['last_month']['solar_consumed'] = last_month_rec['solar_consumed']
        solis_data_dict['metrics']['last_month']['export'] = last_month_rec['export']
        solis_data_dict['metrics']['last_month']['consumed'] = last_month_rec['import'] + last_month_rec['solar_consumed']

    # this year
    # add all month records for last referenced year
    this_year = month_rec['year']

    # reset
    solis_data_dict['metrics']['this_year']['import'] = 0
    solis_data_dict['metrics']['this_year']['solar'] = 0
    solis_data_dict['metrics']['this_year']['solar_consumed'] = 0
    solis_data_dict['metrics']['this_year']['export'] = 0
    solis_data_dict['metrics']['this_year']['consumed'] = 0

    for month_rec in year_data:
        if month_rec['year'] != this_year:
            continue

        solis_data_dict['metrics']['this_year']['import'] += month_rec['import']
        solis_data_dict['metrics']['this_year']['solar'] += month_rec['solar']
        solis_data_dict['metrics']['this_year']['solar_consumed'] += month_rec['solar_consumed']
        solis_data_dict['metrics']['this_year']['export'] += month_rec['export']
        solis_data_dict['metrics']['this_year']['consumed'] += month_rec['import'] + month_rec['solar_consumed']

    # new refresh time
    year_ts = ((70 - dt_now.minute) * 60) + now
    return 


def get_data(solis_config):

    global solis_data_dict
    utils.log_message(
            1,
            "Updating Solis Data"
            )

    get_inverter_day_data(solis_config)
    get_inverter_month_data(solis_config)
    get_inverter_year_data(solis_config)

    # update interval based on last_updated
    # time. This gives a form of dynamic tie-in to 
    # the Solis data by assuming the next refresh is ~5 mins after the 
    # last data we had
    now = int(time.time())
    next_update_ts = solis_data_dict['last_updated'] + 300 + 20
    update_interval = next_update_ts - now

    # negative scenarios
    # fall back to 2-min refresh
    if update_interval < 0:
        update_interval = 120

    # return data and fixed sleep of 5 minutes for refresh
    return solis_data_dict, update_interval



