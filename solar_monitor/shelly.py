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
import copy
import utils

# tracked device and API data
gv_shelly_dict = {}
gv_shelly_dict['last_updated'] = 0
gv_shelly_dict['day_last_updated'] = 0
gv_shelly_dict['month_last_updated'] = 0
gv_shelly_dict['year_last_updated'] = 0

# day, month and year records
gv_shelly_dict['day'] = []
gv_shelly_dict['month'] = []
gv_shelly_dict['year'] = []
gv_shelly_dict['live'] = {}

# timestamps to track the next call
month_ts = 0
year_ts = 0
day_ts = 0


def parse_time(
        datetime_str,
        timezone):
    """
    parses a local string timestamp into an epoch
    value.

    Args:
    datetime_str    - date satring to be parsed
    timezone        - timezone to apply for conversion

    Returns: tuple of epoch timestamp, parsed datetime object
    """

    # naive parse
    dt = dateutil.parser.parse(datetime_str)

    # assert local timezone
    dt = dt.replace(tzinfo = zoneinfo.ZoneInfo(timezone))

    # convert go epoch as God intended
    time_stamp = int(dt.timestamp())

    # return both values
    return time_stamp, dt


def get_shelly_api_usage_data(
        config,
        date_range,
        date_from,
        date_to):
    """
    Calls Shelly historic cloud API to retrieve import/export past usage. 

    Args:
    config     - config dict 
    date_range - Shelly API date range arg
    date_from  - start date
    date_to    - end date

    Returns: dict parsed from API JSON response
    """
    # check if creds are set
    if (
            not config['shelly']['api_host'] or
            not config['shelly']['auth_key'] or
            not config['shelly']['device_id']
            ):
        utils.log_message(
                1,
                'Cloud API creds are not configured.. skipping'
                )
        return None

    # API URL and params
    # two URL variants for 1ph and 3ph
    # device-specific code will select the right one
    shelly_cloud_1p_url = 'https://%s/v2/statistics/power-consumption/em-1p' % (
            config['shelly']['api_host'])
    shelly_cloud_3p_url = 'https://%s/v2/statistics/power-consumption/em-3p' % (
            config['shelly']['api_host'])
    params = {}
    params['auth_key'] = config['shelly']['auth_key']

    # date range
    params['date_range'] = date_range
    if date_from:
        params['date_from'] = date_from

    if date_to:
        params['date_to'] = date_to

    # grid consumption

    # Shell EM/pro can be used as inverter or grid source
    # 1ph variant
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        # single device, 2 channels
        # grid is channel 0
        shelly_cloud_url = shelly_cloud_1p_url
        params['id'] = config['shelly']['device_id']
        params['channel'] = 0

    # 3EM-Pro is only as an inverter (data_source)
    # 3ph variant
    if config['data_source'] == 'shelly-3em-pro':
        # dual devices, 1 channel each
        # grid is device_id, channel 0
        shelly_cloud_url = shelly_cloud_3p_url
        params['id'] = config['shelly']['device_id']
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
                timeout = 20,
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

    # solar production

    # Shell EM/pro can be used as inverter or grid source
    # 1ph variant
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        # single device, 2 channels
        # solar is channel 1
        shelly_cloud_url = shelly_cloud_1p_url
        params['id'] = config['shelly']['device_id']
        params['channel'] = 1

    # 3EM-Pro is only as an inverter (data_source)
    # 3ph variant
    if config['data_source'] == 'shelly-3em-pro':
        # dual devices, 1 channel each
        # solar is device_id_pv, channel 0
        shelly_cloud_url = shelly_cloud_3p_url
        params['id'] = config['shelly']['device_id_pv']
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
                timeout = 20,
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

    # for 1ph, results in 'history' list
    # for 3ph, results in 'sum' list as 'history' list
    # 'sum' list is the total of all 3 phases
    res_list = 'history'
    if config['data_source'] == 'shelly-3em-pro':
        res_list = 'sum'

    data_dict = {}
    for shelly_rec in grid_resp_dict[res_list]:
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
            usage_rec['key'] = key
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
            data_dict[key] = usage_rec

        # mark missing for the possible purge at the end
        if 'missing' in shelly_rec:
            usage_rec['missing'] = True
        else:
            # add on usage for given time period
            # works with repeat hours in DST rollback
            usage_rec['import'] += shelly_rec['consumption'] / 1000
            usage_rec['export'] += shelly_rec['reversed'] / 1000

    # merge in solar production
    for shelly_rec in solar_resp_dict[res_list]:
        # epoch timestamp from shelly API local time 
        ts, ts_dt = parse_time(
                shelly_rec['datetime'],
                solar_resp_dict['timezone'])
        # dict key
        # lowest level is the hour
        # YYYY-MM-DD-HH
        key = '%04d-%02d-%02d-%02d' % (
                ts_dt.year,
                ts_dt.month,
                ts_dt.day,
                ts_dt.hour)

        # retrieve usage rec from dict and 
        # add on solar generation
        # works with repeat hours in DST rollback
        usage_rec = data_dict[key]

        # zero solar if missing
        if 'missing' in shelly_rec:
            solar = 0
        else:
            solar = shelly_rec['consumption'] / 1000

        # solar discard
        # allows for a kwh amount per hour to be thrown away to
        # account for an error on the PV reading
        # has been observed to be about 0.004 kwh per hour
        solar_kwh_discard = config['shelly']['pv_kwh_discard']
        interval = solar_resp_dict['interval']
        if interval == 'day':
            # scale to 24 hours
            solar_kwh_discard *= 24
        elif interval == 'month':
            # scale to 30 days
            solar_kwh_discard *= (24 * 30)

        # apply discard and zero if negative
        solar -= solar_kwh_discard
        solar = max(0, solar)

        # append the solar value 
        usage_rec['solar'] += solar

        # generate/re-generate the consumed fields
        # solar_consumed is zeroed if it goes negative due to the discard
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        if usage_rec['solar_consumed'] < 0:
            usage_rec['solar_consumed'] = 0
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']

        usage_rec['co2'] = (config['environment']['gco2_kwh'] * usage_rec['solar']) / 1000
        usage_rec['trees'] = config['environment']['trees_kwh'] * usage_rec['solar']

    # Purge latter end of missing items
    # Shelly API will include missing items in the data set. 
    # Most of these can be zeroed out but some are in the future.
    # Theswe future values get purged

    # get list of keys separate from dict (for deletion)
    key_list = list(data_dict.keys())

    # key for current time 
    now  = int(time.time()) 
    now_dt = datetime.datetime.fromtimestamp(now)
    now_key = '%04d-%02d-%02d-%02d' % (
            now_dt.year,
            now_dt.month,
            now_dt.day,
            now_dt.hour)

    # scan all keys and remove records equal to the 
    # current hour or later
    # otherwise remove the 'missing' key
    for key in key_list:
        if key >= now_key:
            utils.log_message(
                    utils.gv_verbose,
                    'Purging key:%s (%s)' % (
                        key, 
                        interval
                        )
                    )
            del data_dict[key]
        else:
            if 'missing' in data_dict[key]:
                del data_dict[key]['missing']

    return data_dict


def get_cloud_usage_data(config):
    """
    Combined function to retrieve the last 36 hours,
    30 days and 12 months of historic grid import/export from 
    Shelly cloud.

    Args:
    config     - config dict 

    Populates the results directly in the gv_shelly_dict
    """

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
                'Updating Shelly Day Data'
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
        day_data = get_shelly_api_usage_data(
                config,
                date_range = 'custom',
                date_from = day_ago_str,
                date_to = day_end_str)
        
        if day_data:
            # reset timestamp
            # for :10 past next hour (data may not be present otherwise)
            day_ts = ((70 - dt_today.minute) * 60) + now
            gv_shelly_dict['day'] = day_data

            utils.log_message(
                    1,
                    'Set next day update to %s (%s)' % (
                        day_ts,
                        datetime.datetime.fromtimestamp(day_ts).strftime('%H:%M:%S')
                        )
                    )

            # reformat to list of records
            day_data_list = []
            for key in sorted(day_data.keys()):
                day_data_list.append(day_data[key])

            gv_shelly_dict['day'] = day_data_list[-36:]
            gv_shelly_dict['day_last_updated'] = int(time.time())
    
    if now >= month_ts:
        # last 30 days
        utils.log_message(
                1,
                'Updating Shelly Month Data'
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
        month_data = get_shelly_api_usage_data(
                config,
                date_range = 'custom',
                date_from = month_start_str,
                date_to = month_end_str)

        if month_data:
            # reset timestamp
            # for :10 past next hour (data may not be present otherwise)
            month_ts = ((70 - dt_today.minute) * 60) + now

            utils.log_message(
                    1,
                    'Set next month update to %s (%s)' % (
                        month_ts,
                        datetime.datetime.fromtimestamp(month_ts).strftime('%H:%M:%S')
                        )
                    )

            # reformat to list of records
            month_data_list = []
            for key in sorted(month_data.keys()):
                month_data_list.append(month_data[key])

            gv_shelly_dict['month'] = month_data_list[-30:]
            gv_shelly_dict['month_last_updated'] = int(time.time())

    if now >= year_ts:
        # last several months or so
        # will query all of previous year to today 
        # seems to only work if stretch back 300 days
        utils.log_message(
                1,
                'Updating Shelly Year Data'
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
        year_data = get_shelly_api_usage_data(
                config,
                date_range = 'custom',
                date_from = last_year_start_str,
                date_to = year_end_str)
        
        if year_data:
            # reset timestamp
            # for :10 past next hour (data may not be present otherwise)
            year_ts = ((70 - dt_today.minute) * 60) + now
            utils.log_message(
                    1,
                    'Set next year update to %s (%s)' % (
                        year_ts,
                        datetime.datetime.fromtimestamp(year_ts).strftime('%H:%M:%S')
                        )
                    )

            # reformat to list of records
            year_data_list = []
            for key in sorted(year_data.keys()):
                year_data_list.append(year_data[key])

            gv_shelly_dict['year'] = year_data_list[-12:]
            gv_shelly_dict['year_last_updated'] = int(time.time())

    return


def get_cloud_live_data(config):
    """
    This will check the grid_source and data_source fields 
    in config and call into the Shelly Cloud API for live import and 
    PV generation data

    Args:
    config     - config dict 

    Writes results direct to the gv_shelly_dict
    """
    global gv_shelly_dict

    # check if creds are set
    if (
            not config['shelly']['api_host'] or
            not config['shelly']['auth_key'] or
            not config['shelly']['device_id']
            ):
        utils.log_message(
                1,
                'Cloud API creds are not configured.. skipping'
                )
        return 

    now  = int(time.time())
    now_dt = datetime.datetime.fromtimestamp(now)
    sleep_period = (config['shelly']['time_slot'] - now_dt.second) % 10
    if sleep_period > 0:
        utils.log_message(
                1,
                'Sleep %ds for 10s boundary :0%d' % (
                    sleep_period,
                    config['shelly']['time_slot'])
                )
        time.sleep(sleep_period)

    shelly_cloud_url = 'https://%s/v2/devices/api/get?auth_key=%s' % (
            config['shelly']['api_host'], 
            config['shelly']['auth_key'])

    headers = {}
    headers['Content-Type'] = 'application/json'

    request = {}
    request['ids'] = []
    request['select'] = ['status']

    # variants
    if config['data_source'] == 'shelly-em':
        # 1-phase inverter function single device
        request['ids'].append(config['shelly']['device_id'])
    elif config['grid_source'] == 'shelly-em':
        # 1-phase live only
        request['ids'].append(config['shelly']['device_id'])
    elif config['data_source'] == 'shelly-3em-pro':
        # 3-phase inverter 2 devices
        request['ids'].append(config['shelly']['device_id'])
        request['ids'].append(config['shelly']['device_id_pv'])
    else:
        utils.log_message(
                1,
                'Shelly variant (%s) is not valid.. skipping device call' % (
                    config['data_source']
                    )
                )
        return

    try:
        utils.log_message(
                utils.gv_verbose,
                'Calling Shelly Cloud API.. url:%s request:%s' % (
                    shelly_cloud_url,
                    request
                    )
                )
        resp = requests.post(
                shelly_cloud_url, 
                timeout = 20,
                headers = headers,
                json = request)
        resp_dict = resp.json()

    except:
        utils.log_message(
                1,
                'Shelly Cloud API Call to %s, request %s failed' % (
                    shelly_cloud_url,
                    request
                    )
                )
        return 

    utils.log_message(
            utils.gv_verbose,
            'API Response (%s)\n%s\n' % (
                request, 
                json.dumps(resp_dict, indent = 4),
                )
            )

    # congestion detection
    if 'error' in resp_dict:
        utils.log_message(
                1,
                'Shelly Cloud API congestion'                 
                )
        return 

    # variants
    if config['data_source'] == 'shelly-em':
        # single device, two em1 channels
        grid = resp_dict[0]['status']['em1:0']['act_power'] / 1000
        solar = resp_dict[0]['status']['em1:1']['act_power'] / 1000
    elif config['grid_source'] == 'shelly-em':
        # single device, two em1 channels
        grid = resp_dict[0]['status']['em1:0']['act_power'] / 1000
        solar = resp_dict[0]['status']['em1:1']['act_power'] / 1000
    elif config['data_source'] in ['shelly-3em-pro']:
        # two devices, single em channel each
        # total_act_power is the sum of all 3ph readings
        grid = resp_dict[0]['status']['em:0']['total_act_power'] / 1000
        solar = resp_dict[1]['status']['em:0']['total_act_power'] / 1000
    else:
        # Apollo alarms
        grid = 12.01 
        solar = 12.02

    # update live data
    # timestamp taken from status record from Shelly API 
    # (when they last updated) may not always be present
    now = int(time.time())
    if 'ts' in resp_dict[0]['status']:
        gv_shelly_dict['last_updated'] = int(resp_dict[0]['status']['ts'])
    else:
        gv_shelly_dict['last_updated'] = now

    # generate a delayed mesage for gaps over 2 mins
    message = ''
    if now - gv_shelly_dict['last_updated'] >= 120:
        message = ' (delayed)'

    live_rec = gv_shelly_dict['live']

    time_str = datetime.datetime.fromtimestamp(
            gv_shelly_dict['last_updated']).strftime('%H:%M:%S')
    live_rec['title'] = 'Live Usage @%s%s' % (time_str, message)

    # render into separate values for import and export
    if grid >= 0:
        grid_import = grid
        grid_export = 0
    else:
        grid_import = 0
        grid_export = grid * -1

    # for solar, discard zero readings below 10W
    # gets rid of noise readings at night
    if solar <= 0.010:
        solar = 0

    # populate the sanitised and derived values
    live_rec['import'] = grid_import
    live_rec['export'] = grid_export
    live_rec['solar'] = solar

    live_rec['solar_consumed'] = max(0, live_rec['solar'] - live_rec['export'])
    live_rec['consumed'] = live_rec['solar_consumed'] + live_rec['import']

    live_rec['co2'] = (config['environment']['gco2_kwh'] * solar) / 1000
    live_rec['trees'] = config['environment']['trees_kwh'] * solar

    utils.log_message(
            1,
            'Live data: import:%.3f export:%.3f solar:%.3f' % (
                live_rec['import'],
                live_rec['export'],
                live_rec['solar'],
                )
            )

    return


def get_data(config):
    """
    Gets inverter data. This is the module common function 
    called by the parent solar_monnitor.py script. It manages 
    all lower level calls for day, month and year and returns the 
    results in a common format dict object

    Args:
    config    - gloval config

    Returns: tuple of the data dict and refresh interval (fixed at 5 seconds)
    """
    global gv_shelly_dict

    get_cloud_live_data(config)
    get_cloud_usage_data(config)

    utils.log_message(
            utils.gv_verbose,
            'Shelly Data Dict:\n%s' % (
                json.dumps(
                    gv_shelly_dict, 
                    indent = 4)
                ) 
            )

    # return dep copy of data
    # and a fixed 5-sec refresh
    # live data updates are every 10 but we need to nudge it 
    # easlier to allow thew time_slot sleep to align
    return copy.deepcopy(gv_shelly_dict), 5
