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
gv_shelly_dict = {}
gv_shelly_dict['last_updated'] = 0

# day, month and year records
gv_shelly_dict['day'] = {}
gv_shelly_dict['month'] = {}
gv_shelly_dict['year'] = {}

gv_shelly_dict['live'] = {}
gv_shelly_dict['live']['title'] = 'Now'
gv_shelly_dict['live']['import'] = 0
gv_shelly_dict['live']['export'] = 0
gv_shelly_dict['live']['solar'] = 0

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
                utils.gv_verbose,
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

    # populate consumption records
    data_dict = {}
    for shelly_rec in grid_resp_dict['history']:
        # skip any missing records
        # and note partial data scenario
        if ('missing' in shelly_rec and 
            shelly_rec['missing']):
            continue

        # epoch timestamp from shelly API local time 
        ts, ts_dt = parse_time(
                shelly_rec['datetime'],
                grid_resp_dict['timezone'])

        # dict key
        # lowest level is the hour
        # YYYY-MM-DD-HH
        key = '%04d-%02d-%02d-%02d' % (
                ts_dt.year,
                ts_dt.month,
                ts_dt.day,
                ts_dt.hour)

        # pull existing rec from dict or create 
        # new one. Most of the time its a new one we create
        # But for DST roll-back (winter), we see a repeat of 
        # data for the same hour
        if key in data_dict:
            usage_rec = data_dict[key]
        else:
            usage_rec = {}
            usage_rec['import'] = 0
            usage_rec['export'] = 0

            # formatted time periods
            usage_rec['year'] = '%04d' %(
                    ts_dt.year)
            usage_rec['month'] = ts_dt.strftime('%b')
            usage_rec['day'] = ts_dt.day
            usage_rec['hour'] = ts_dt.hour

            # store in dict
            data_dict[key] = usage_rec

        # add on usage for given time period
        # works with repeat hours in DST rollback
        usage_rec['import'] += shelly_rec['consumption'] / 1000
        usage_rec['export'] += shelly_rec['reversed'] / 1000

    return data_dict


def get_cloud_data(config):

    global gv_shelly_dict
    global month_ts
    global year_ts
    global day_ts

    now = int(time.time())
    dt_today = datetime.datetime.today() 
    dt_yesterday = dt_today - datetime.timedelta(days = 1)

    if now >= day_ts:
        # last 36 hours
        utils.log_message(
                1,
                "Updating Shelly Day Data"
                )

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
        
        # using configured hour discard
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
            gv_shelly_dict['day'] = day_data
    
    if now >= month_ts:
        # last 30 days
        utils.log_message(
                1,
                "Updating Shelly Month Data"
                )

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
        
        # using configured day discard
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

            gv_shelly_dict['month'] = month_data

    if now >= year_ts:
        # last several months or so
        # will query all of previous year to today 
        # seems to only work if stretch back 300 days
        utils.log_message(
                1,
                "Updating Shelly Year Data"
                )

        last_year = dt_month_start - datetime.timedelta(days = 300)
        last_year_start_str = '%04d-%02d-01 00:00:00' % (
                    last_year.year, 
                    last_year.month
                    )
        year_end_str = '%04d-12-31 23:59:59' % (
                    dt_today.year
                    )
        
        # using configured day discard times 30
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
            gv_shelly_dict['year'] = year_data

    return


def get_shelly_em_live_data(config):

    utils.log_message(
            1,
            "Updating Shelly EM Live Data"
            )

    device_url = 'http://%s/status' % (config['shelly']['device_host'])
    basic =  requests.auth.HTTPBasicAuth(
            config['shelly']['device_username'], 
            config['shelly']['device_password']) 

    try:
        utils.log_message(
                utils.gv_verbose,
                'Calling Shelly EM Device API.. url:%s' % (
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
                'Shelly EM Device API Call to %s failed' % (
                    device_url,
                    )
                )
        return None, None

    utils.log_message(
            utils.gv_verbose,
            'Device API Response\n%s\n' % (
                json.dumps(device_resp_dict, indent = 4),
                )
            )

    # convert to kW
    grid = device_resp_dict['emeters'][0]['power'] / 1000
    solar = device_resp_dict['emeters'][1]['power'] / 1000

    return grid, solar


def get_shelly_pro_em_live_data(config):

    utils.log_message(
            1,
            "Updating Shelly Pro EM Live Data"
            )

    # HTTP digest based auth
    digest_auth =  requests.auth.HTTPDigestAuth(
            config['shelly']['device_username'], 
            config['shelly']['device_password']) 

    # CT 0 (Grid)
    device_url = 'http://%s/rpc/EM1.GetStatus?id=0' % (config['shelly']['device_host'])

    try:
        utils.log_message(
                utils.gv_verbose,
                'Calling Shelly Pro EM Device API.. url:%s' % (
                    device_url
                    )
                )
        resp = requests.get(
                device_url, 
                auth = digest_auth)
        grid_resp_dict = resp.json()
    except:
        utils.log_message(
                1,
                'Shelly EM Device API Call to %s failed' % (
                    device_url,
                    )
                )
        return None, None

    utils.log_message(
            utils.gv_verbose,
            'Device API Response\n%s\n' % (
                json.dumps(grid_resp_dict, indent = 4),
                )
            )

    # CT 1 (Solar)
    device_url = 'http://%s/rpc/EM1.GetStatus?id=1' % (config['shelly']['device_host'])

    try:
        utils.log_message(
                utils.gv_verbose,
                'Calling Shelly Pro EM Device API.. url:%s' % (
                    device_url
                    )
                )
        resp = requests.get(
                device_url, 
                auth = digest_auth)
        solar_resp_dict = resp.json()
    except:
        utils.log_message(
                1,
                'Shelly EM Device API Call to %s failed' % (
                    device_url,
                    )
                )
        return None, None

    utils.log_message(
            utils.gv_verbose,
            'Device API Response\n%s\n' % (
                json.dumps(solar_resp_dict, indent = 4),
                )
            )
    # convert to kW
    grid = grid_resp_dict['act_power'] / 1000
    solar = solar_resp_dict['act_power'] / 1000

    return grid, solar


def get_live_data(config):
    global gv_shelly_dict

    if not config['shelly']['device_host']:
        utils.log_message(
                1,
                "Shelly Device Host is not configured.. skipping device call"
                )
        return

    if config['grid_source'] == 'shelly-em':
        grid, solar = get_shelly_em_live_data(config)
    elif config['grid_source'] == 'shelly-pro':
        grid, solar = get_shelly_pro_em_live_data(config)
    else:
        utils.log_message(
                1,
                "Shelly variant (%s) is not valid.. skipping device call" % (
                    config['data_source']
                    )
                )
        return

    if grid is None and solar is None:
        utils.log_message(
                1,
                "Live data call failed"
                )
        return

    # render into separate values for import and export
    if grid >= 0:
        grid_import = grid
        grid_export = 0
    else:
        grid_import = 0
        grid_export = grid * -1

    # for solar, zero readings below 10W
    if solar <= 0.010:
        solar = 0

    # update live metrics
    gv_shelly_dict['last_updated'] = int(time.time())
    live_metrics_rec = gv_shelly_dict['live']

    time_str = datetime.datetime.fromtimestamp(
            gv_shelly_dict['last_updated']).strftime('%H:%M:%S')
    live_metrics_rec['title'] = 'Live Usage @%s' % (time_str)

    live_metrics_rec['import'] = grid_import
    live_metrics_rec['export'] = grid_export
    live_metrics_rec['solar'] = solar

    utils.log_message(
            1,
            "Shelly Device: import:%f export:%f solar:%f" % (
                live_metrics_rec['import'],
                live_metrics_rec['export'],
                live_metrics_rec['solar'],
                )
            )

    return


def get_data(config):

    global gv_shelly_dict

    get_live_data(config)

    utils.log_message(
            1,
            "Checking Shelly Cloud Data for updates.. timestamps: day:%s month:%s year:%s" % (
                day_ts,
                month_ts,
                year_ts
                )
            )
    get_cloud_data(config)

    utils.log_message(
            utils.gv_verbose,
            'Shelly Data Dict:\n%s' % (
                json.dumps(
                    gv_shelly_dict, 
                    indent = 4)
                ) 
            )

    # return data and fixed sleep of 10 seconds for refresh
    return gv_shelly_dict, 10
