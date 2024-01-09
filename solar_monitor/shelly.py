import argparse
import requests
import json
import os
import sys
import traceback
import time
import datetime
import dateutil.parser
import zoneinfo
import random
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
gv_data_dict['metrics']['live']['title'] = 'Now'
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
day_ts = 0


def parse_time(
        datetime_str,
        timezone):

    # naive parse
    dt = dateutil.parser.parse(datetime_str)

    # assert local timezone
    dt = dt.replace(tzinfo = zoneinfo.ZoneInfo(timezone))

    # convert go epoch as God intended
    time_stamp = int(dt.timestamp())

    # return both values
    return time_stamp, dt


def get_shelly_api_data(
        config,
        date_range,
        date_from,
        date_to):

    # check if creds are set
    if (
            not config['shelly']['api_host'] or
            not config['shelly']['auth_key'] or
            not config['shelly']['device_id']
            ):
        utils.log_message(
                1,
                "Cloud API creds are not configured.. skipping"
                )
        return None

    # API URL and params
    shelly_cloud_url = 'https://%s/v2/statistics/power-consumption/em-1p' % (
            config['shelly']['api_host'])
    params = {}
    params['id'] = config['shelly']['device_id']
    params['auth_key'] = config['shelly']['auth_key']
    params['date_range'] = date_range

    if date_from:
        params['date_from'] = date_from

    if date_to:
        params['date_to'] = date_to

    # channel 0 (grid consumption and return)
    params['channel'] = 0
    try:
        utils.log_message(
                1,
                'Calling Shelly Cloud API.. url:%s params:%s' % (
                    shelly_cloud_url,
                    params
                    )
                )
        resp = requests.get(
                shelly_cloud_url, 
                data = params)
        grid_resp_dict = resp.json()

    except:
        utils.log_message(
                1,
                'Shelly Cloud API Call to %s, params %s failed' % (
                    shelly_cloud_url,
                    params
                    )
                )
        return None

    utils.log_message(
            utils.gv_verbose,
            'API Response (%s)\n%s\n' % (
                params, 
                json.dumps(grid_resp_dict, indent = 4),
                )
            )

    # channel 1 (solar production)
    params['channel'] = 1
    try:
        resp = requests.get(
                shelly_cloud_url, 
                data = params)
        solar_resp_dict = resp.json()
    except:
        utils.log_message(
                1,
                'Shelly Cloud API Call to %s, params %s failed' % (
                    shelly_cloud_url,
                    params
                    )
                )
        return None


    utils.log_message(
            utils.gv_verbose,
            'API Response (%s)\n%s\n' % (
                params, 
                json.dumps(solar_resp_dict, indent = 4),
                )
            )

    # populate consumption records
    data_dict = {}
    partial_data = False
    for shelly_rec in grid_resp_dict['history']:
        # skip any missing records
        # and note partial data scenario
        if ('missing' in shelly_rec and 
            shelly_rec['missing']):
            partial_data = True
            continue

        # epoch timestamp from shelly API local time 
        ts, ts_dt = parse_time(
                shelly_rec['datetime'],
                grid_resp_dict['timezone'])

        # pull existing rec from dict or create 
        # new one. Most of the time its a new one we create
        # But for DST roll-back (winter), we see a repeat of 
        # data for the same hour
        if ts in data_dict:
            usage_rec = data_dict[ts]
        else:
            usage_rec = {}
            usage_rec['import'] = 0
            usage_rec['export'] = 0
            usage_rec['solar'] = 0

            # formatted time periods
            usage_rec['year'] = '%04d' %(
                    ts_dt.year)
            usage_rec['month'] = ts_dt.strftime('%b')
            usage_rec['day'] = ts_dt.day
            usage_rec['hour'] = ts_dt.hour

            # store in dict
            data_dict[ts] = usage_rec

        # add on usage for given time period
        # works with repeat hours in DST rollback
        usage_rec['import'] += shelly_rec['consumption'] / 1000
        usage_rec['export'] += shelly_rec['reversed'] / 1000

    # merge in solar production
    for shelly_rec in solar_resp_dict['history']:
        # skip any missing records
        # and note partial data scenario
        if ('missing' in shelly_rec and 
            shelly_rec['missing']):
            partial_data = True
            continue

        # epoch timestamp from shelly API local time 
        ts, ts_dt = parse_time(
                shelly_rec['datetime'],
                grid_resp_dict['timezone'])

        # retrieve usage rec from dict and 
        # add on solar generation
        # works with repeat hours in DST rollback
        usage_rec = data_dict[ts]
        usage_rec['solar'] += shelly_rec['consumption'] / 1000

        # generate/re-generate the consumed fields
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']

        # environmental metrics
        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

    # reformat to list of records
    data_list = []
    for key in sorted(data_dict.keys()):
        data_list.append(data_dict[key])

    return data_list


def get_cloud_data(config):

    global gv_data_dict
    global month_ts
    global year_ts
    global day_ts

    utils.log_message(
            1,
            "Updating Shelly Cloud Data"
            )

    utils.log_message(
            1,
            'Cloud API Refresh timestamps.. day:%d month:%d year:%d' % (
                day_ts,
                month_ts,
                year_ts)
            )

    now = int(time.time())
    dt_today = datetime.datetime.today() 
    dt_yesterday = dt_today - datetime.timedelta(days = 1)

    if now >= day_ts:
        # last 36 hours
        dt_36h_ago = dt_today - datetime.timedelta(hours = 36)
        day_ago_str = '%04d-%02d-%02d %02d:00:00' % (
                    dt_36h_ago.year, 
                    dt_36h_ago.month, 
                    dt_36h_ago.day,
                    dt_36h_ago.hour,
                    )
        day_end_str = '%04d-%02d-%02d 23:59:59' % (
                    dt_today.year, 
                    dt_today.month, 
                    dt_today.day
                    )
        
        day_data = get_shelly_api_data(
                config,
                date_range = 'custom',
                date_from = day_ago_str,
                date_to = day_end_str)
        
        if day_data:
            # reset timestamp
            # for :10 past next hour
            day_ts = ((70 - dt_today.minute) * 60) + now

            utils.log_message(
                    utils.gv_verbose,
                    'last 24h API Data\n%s\n' % (
                        json.dumps(
                            day_data, 
                            indent = 4),
                        )
                    )
            gv_data_dict['day'] = day_data
    
    if now >= month_ts:
        # last 30 days
        dt_month_start = dt_today - datetime.timedelta(days = 30)
        month_start_str = '%04d-%02d-%02d 00:00:00' % (
                    dt_month_start.year, 
                    dt_month_start.month, 
                    dt_month_start.day
                    )
        month_end_str = '%04d-%02d-%02d 23:59:59' % (
                    dt_today.year, 
                    dt_today.month, 
                    dt_today.day
                    )
        
        month_data = get_shelly_api_data(
                config,
                date_range = 'custom',
                date_from = month_start_str,
                date_to = month_end_str)

        if month_data:
            # reset timestamp
            # for :10 past next hour
            month_ts = ((70 - dt_today.minute) * 60) + now
            utils.log_message(
                    utils.gv_verbose,
                    'Month API Data\n%s\n' % (
                        json.dumps(
                            month_data, 
                            indent = 4),
                        )
                    )

            # truncate to last 30 days as we can overflow into 31
            month_data = month_data[-30:]
        
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

    if now >= year_ts:
        # last several months or so
        # will query all of previous year to today 
        # seems to only work if stretch back 300 days
        last_year = dt_month_start - datetime.timedelta(days = 300)
        last_year_start_str = '%04d-%02d-01 00:00:00' % (
                    last_year.year, 
                    last_year.month
                    )
        year_end_str = '%04d-12-31 23:59:59' % (
                    dt_today.year
                    )
        
        year_data = get_shelly_api_data(
                config,
                date_range = 'custom',
                date_from = last_year_start_str,
                date_to = year_end_str)
        
        if year_data:
            # reset timestamp
            # for :10 past next hour
            year_ts = ((70 - dt_today.minute) * 60) + now
            utils.log_message(
                    utils.gv_verbose,
                    'Year API Data\n%s\n' % (
                        json.dumps(
                            year_data, 
                            indent = 4),
                        )
                    )
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

            # last 12 months 
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

    return


def get_live_data(config):

    utils.log_message(
            1,
            "Updating Shelly Live Data"
            )

    if not config['shelly']['device_host']:
        utils.log_message(
                1,
                "Shelly Device Host is not configured.. skipping device call"
                )
        return

    device_url = 'http://%s/status' % (config['shelly']['device_host'])
    basic =  requests.auth.HTTPBasicAuth(
            config['shelly']['device_username'], 
            config['shelly']['device_password']) 

    try:
        utils.log_message(
                1,
                'Calling Shelly Device API.. url:%s' % (
                    device_url
                    )
                )
        resp = requests.get(
                device_url, 
                auth = basic)
        device_resp_dict = resp.json()
    except:
        utils.log_message(
                1,
                'Shelly Device API Call to %s failed' % (
                    device_url,
                    )
                )
        return

    utils.log_message(
            utils.gv_verbose,
            'Device API Response\n%s\n' % (
                json.dumps(device_resp_dict, indent = 4),
                )
            )

    # convert to kW
    grid = device_resp_dict['emeters'][0]['power'] / 1000
    solar = device_resp_dict['emeters'][1]['power'] / 1000

    gv_data_dict['last_updated'] = int(time.time())
    time_str = datetime.datetime.fromtimestamp(
            gv_data_dict['last_updated']).strftime('%H:%M:%S')
    gv_data_dict['metrics']['live']['title'] = 'Live Usage @%s' % (time_str)

    if grid >= 0:
        gv_data_dict['metrics']['live']['import'] = grid
        gv_data_dict['metrics']['live']['export'] = 0
    else:
        gv_data_dict['metrics']['live']['import'] = 0
        gv_data_dict['metrics']['live']['export'] = grid * -1

    if solar >= 0.010:
        gv_data_dict['metrics']['live']['solar'] = solar
    else:
        gv_data_dict['metrics']['live']['solar'] = 0

    gv_data_dict['metrics']['live']['solar_consumed'] = gv_data_dict['metrics']['live']['solar'] - gv_data_dict['metrics']['live']['export']
    gv_data_dict['metrics']['live']['consumed'] = gv_data_dict['metrics']['live']['import'] + gv_data_dict['metrics']['live']['solar_consumed'] 

    gv_data_dict['metrics']['live']['co2'] = (config['environment']['gco2_kwh'] * solar) / 1000
    gv_data_dict['metrics']['live']['trees'] = config['environment']['trees_kwh'] * solar

    utils.log_message(
            1,
            "Shelly Device: import:%f export:%f solar:%f consumed:%f" % (
                gv_data_dict['metrics']['live']['import'],
                gv_data_dict['metrics']['live']['export'],
                gv_data_dict['metrics']['live']['solar'],
                gv_data_dict['metrics']['live']['consumed'],
                )
            )

    return


def get_data(config):

    global gv_data_dict

    utils.log_message(
            1,
            "Updating Shelly Data"
            )

    get_live_data(config)
    get_cloud_data(config)

    # return data and fixed sleep of 5 seconds for refresh
    return gv_data_dict, 5



