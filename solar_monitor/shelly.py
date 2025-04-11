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
gv_shelly_dict['total'] = {}

gv_shelly_dict['total']['import'] = 0
gv_shelly_dict['total']['export'] = 0

# timestamps to track the next cloud usage call
# and a snapshot of the live data for the same time
gv_cloud_refresh_ts = 0
gv_total_snapshot_rec = None # will be set on each live call


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

    # Shelly EM/pro can be used as inverter or grid source
    # 1ph variant
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        # single device, 2 channels
        # grid is channel 0
        shelly_cloud_url = shelly_cloud_1p_url
        params['id'] = config['shelly']['device_id'].strip()
        params['channel'] = 0

    # 3EM-Pro is only as an inverter (data_source)
    # 3ph variant but can be used for grid only, PV only or both
    # so device_id might be unset
    if config['data_source'] == 'shelly-3em-pro':
        # dual devices, 1 channel each
        # grid is device_id, channel 0
        shelly_cloud_url = shelly_cloud_3p_url
        params['id'] = config['shelly']['device_id'].strip()
        params['channel'] = 0

    grid_resp_dict = None
    if params['id']:
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
        params['id'] = config['shelly']['device_id'].strip()
        params['channel'] = 1

    # 3EM-Pro is only as an inverter (data_source)
    # 3ph variant but can be used for grid only, PV only or both
    # so device_id_pv might be unset
    if config['data_source'] == 'shelly-3em-pro':
        # dual devices, 1 channel each
        # solar is device_id_pv, channel 0
        shelly_cloud_url = shelly_cloud_3p_url
        params['id'] = config['shelly']['device_id_pv'].strip()
        params['channel'] = 0

    solar_resp_dict = None
    if params['id']:
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

    if grid_resp_dict:
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
                usage_rec['missing'] = True
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

            # populate grid detail if present
            if not 'missing' in shelly_rec:
                # remove default missing key
                if 'missing' in usage_rec:
                    del usage_rec['missing']

                # shelly API returns in Wh
                # convert to kWh 
                grid_import = shelly_rec['consumption'] / 1000
                grid_export = shelly_rec['reversed'] / 1000

                # scale by grid factor
                # will normally be set to 1 but in some 3phase setups, 
                # there will be parallel trunk cables and the CT clamps will fit only
                # on one of the cables. This will cause a 2x or 3x factor to be applied 
                # as configured

                if 'grid_scale_factor' in config['shelly']:
                    grid_scale_factor = config['shelly']['grid_scale_factor']
                else:
                    # default to 1
                    grid_scale_factor = 1

                grid_import *= grid_scale_factor
                grid_export *= grid_scale_factor

                # add on usage for given time period
                # works with repeat hours in DST rollback
                usage_rec['import'] += grid_import
                usage_rec['export'] += grid_export

    # merge in solar production
    if solar_resp_dict:
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

            # pull existing rec from dict or create 
            # new one. Most of the time its a new one we create
            # But for DST roll-back (winter), we see a repeat of 
            # data for the same hour
            if key in data_dict:
                usage_rec = data_dict[key]
            else:
                usage_rec = {}
                usage_rec['key'] = key
                usage_rec['missing'] = True
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

            # populate pv detail if present
            if not 'missing' in shelly_rec:
                # remove default missing key
                if 'missing' in usage_rec:
                    del usage_rec['missing']

                # shelly API returns in Wh
                # convert to kWh 
                solar = shelly_rec['consumption'] / 1000

                # solar discard
                # allows for a kwh amount per hour to be thrown away to
                # account for an error on the PV reading
                # has been observed to be about 0.004 kwh per hour
                # only applied for 12 hours a day however
                solar_kwh_discard = config['shelly']['pv_kwh_discard']
                interval = solar_resp_dict['interval']
                if interval == 'day':
                    # scale to 12 hours
                    solar_kwh_discard *= 12
                elif interval == 'month':
                    # scale to 12x30 days
                    solar_kwh_discard *= (12 * 30)

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

    # scan all keys and remove records 
    # beyond the current hour 
    # otherwise remove the 'missing' key
    for key in key_list:
        if key > now_key:
            utils.log_message(
                    utils.gv_verbose,
                    'Purging key:%s' % (key)
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
    global gv_cloud_refresh_ts

    now = int(time.time())
    dt_today = datetime.datetime.today() 
    dt_yesterday = dt_today - datetime.timedelta(days = 1)

    if now < gv_cloud_refresh_ts:
        return

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
    
    day_data = get_shelly_api_usage_data(
            config,
            date_range = 'custom',
            date_from = day_ago_str,
            date_to = day_end_str)
    
    if day_data:
        # reformat to list of records
        day_data_list = []
        for key in sorted(day_data.keys()):
            day_data_list.append(day_data[key])

        gv_shelly_dict['day'] = day_data_list[-36:]
        gv_shelly_dict['day_last_updated'] = int(time.time())
    
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
    
    month_data = get_shelly_api_usage_data(
            config,
            date_range = 'custom',
            date_from = month_start_str,
            date_to = month_end_str)

    if month_data:
        # reformat to list of records
        month_data_list = []
        for key in sorted(month_data.keys()):
            month_data_list.append(month_data[key])

        gv_shelly_dict['month'] = month_data_list[-30:]
        gv_shelly_dict['month_last_updated'] = int(time.time())

    # last several months or so
    # will query end of current month and go back 12 months
    # seems to only work if stretch back 300 days
    # trying 365 or >300 and it ends several months earlier or gives a 
    # current month with nothing or very low usage
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
    
    year_data = get_shelly_api_usage_data(
            config,
            date_range = 'custom',
            date_from = last_year_start_str,
            date_to = month_end_str)
    
    if year_data:
        # reformat to list of records
        year_data_list = []
        for key in sorted(year_data.keys()):
            year_data_list.append(year_data[key])

        gv_shelly_dict['year'] = year_data_list[-12:]
        gv_shelly_dict['year_last_updated'] = int(time.time())

    if day_data and month_data and year_data:
        # reset timestamp
        # for :10 past next hour (data may not be present otherwise)
        gv_cloud_refresh_ts = ((70 - dt_today.minute) * 60) + now
        utils.log_message(
                1,
                'Set next cloud update to %s (%s)' % (
                    gv_cloud_refresh_ts,
                    datetime.datetime.fromtimestamp(
                        gv_cloud_refresh_ts).strftime('%H:%M:%S')
                    )
                )
    else:
        # retry in mins
        gv_cloud_refresh_ts = now + 60
        utils.log_message(
                1,
                'Errors encountered with cloud API calls.. set next cloud update to %s (%s)' % (
                    gv_cloud_refresh_ts,
                    datetime.datetime.fromtimestamp(
                        gv_cloud_refresh_ts).strftime('%H:%M:%S')
                    )
                )

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
    global gv_total_snapshot_rec

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
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        # 1-phase inverter function single device
        request['ids'].append(config['shelly']['device_id'])
    elif config['data_source'] == 'shelly-3em-pro':
        # 3-phase inverter 2 devices
        # but we tolerate either one missing
        # also note the slot positions of each
        if config['shelly']['device_id']:
            request['ids'].append(config['shelly']['device_id'])
        if config['shelly']['device_id_pv']:
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
    grid = 0
    solar = 0
    total_grid_import = 0
    total_grid_export = 0
    total_solar = 0

    for status_rec in resp_dict:
        if (config['data_source'] == 'shelly-em' or 
            config['grid_source'] == 'shelly-em'):

            if status_rec['id'] == config['shelly']['device_id']:
                # single device, two em1 channels
                grid = status_rec['status']['em1:0']['act_power'] / 1000
                solar = status_rec['status']['em1:1']['act_power'] / 1000
                total_grid_import = status_rec['status']['em1data:0']['total_act_energy'] / 1000
                total_grid_export = status_rec['status']['em1data:0']['total_act_ret_energy'] / 1000
                total_solar = status_rec['status']['em1data:1']['total_act_energy'] / 1000

        elif (config['data_source'] in ['shelly-3em-pro']):
            # two devices, single em channel each
            # total_act_power is the sum of all 3ph readings

            if status_rec['id'] == config['shelly']['device_id']:
                grid = status_rec['status']['em:0']['total_act_power'] / 1000
                total_grid_import = status_rec['status']['emdata:0']['total_act'] / 1000
                total_grid_export = status_rec['status']['emdata:0']['total_act_ret'] / 1000

            if status_rec['id'] == config['shelly']['device_id_pv']:
                solar = status_rec['status']['em:0']['total_act_power'] / 1000
                total_solar = status_rec['status']['emdata:0']['total_act'] / 1000

    # update live data
    # timestamp taken from status record from Shelly API 
    # (when they last updated) may not always be present
    now = int(time.time())
    if 'ts' in resp_dict[0]['status']:
        gv_shelly_dict['last_updated'] = int(resp_dict[0]['status']['ts'])
    else:
        gv_shelly_dict['last_updated'] = now

    live_rec = gv_shelly_dict['live']
    live_rec['ts'] = gv_shelly_dict['last_updated']

    # broken out values for local time
    live_dt = datetime.datetime.fromtimestamp(live_rec['ts'])
    live_rec['year'] = '%04d' %(
                        live_dt.year)
    live_rec['month'] = live_dt.strftime('%b')
    live_rec['day'] = live_dt.day
    live_rec['hour'] = live_dt.hour
    live_rec['minute'] = live_dt.minute
    live_rec['second'] = live_dt.second

    # zero values if delayed longer thn 2 minutes
    if now - gv_shelly_dict['last_updated'] >= 120:
        grid = 0
        solar = 0

    # render into separate values for import and export
    if grid >= 0:
        grid_import = grid
        grid_export = 0
    else:
        grid_import = 0
        grid_export = grid * -1

    # scale by grid factor
    # will normally be set to 1 but in some 3phase setups, 
    # there will be parallel trunk cables and the CT clamps will fit only
    # on one of the cables. This will cause a 2x or 3x factor to be applied 
    # as configured
    if 'grid_scale_factor' in config['shelly']:
        grid_scale_factor = config['shelly']['grid_scale_factor']
    else:
        # default to 1
        grid_scale_factor = 1

    grid_import *= grid_scale_factor
    grid_export *= grid_scale_factor
    total_grid_import *= grid_scale_factor
    total_grid_export *= grid_scale_factor

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

    # total accumulated values for import, export and solar
    total_rec = gv_shelly_dict['total']
    total_rec['import'] = total_grid_import
    total_rec['export'] = total_grid_export
    total_rec['solar'] = total_solar

    total_rec['solar_consumed'] = max(0, total_rec['solar'] - total_rec['export'])
    total_rec['consumed'] = total_rec['solar_consumed'] + total_rec['import']

    total_rec['co2'] = (config['environment']['gco2_kwh'] * total_rec['solar']) / 1000
    total_rec['trees'] = config['environment']['trees_kwh'] * total_rec['solar']

    # calculate delta values since last live update
    import_delta = 0
    export_delta = 0
    solar_delta = 0

    # apply delta values to the last hour, day and month records
    # if we actually have this data
    if (gv_total_snapshot_rec and 
        len(gv_shelly_dict['day']) > 0 and
        len(gv_shelly_dict['month']) > 0 and
        len(gv_shelly_dict['year']) > 0):

        # calculate deltas
        import_delta = total_rec['import'] - gv_total_snapshot_rec['import']
        export_delta = total_rec['export'] - gv_total_snapshot_rec['export']

        # solar treated differently. Only set to what we measure if solar 
        # is actually present. Otherwise, we zero it out
        # this is the same false reading on low values, sometimes seen at night
        if live_rec['solar'] > 0:
            solar_delta = total_rec['solar'] - gv_total_snapshot_rec['solar']
        else:
            solar_delta = 0

        # apply offsets for the this hour and recalc derived values 
        latest_hour_rec = gv_shelly_dict['day'][-1]
        latest_hour_rec['import'] += import_delta
        latest_hour_rec['export'] += export_delta
        latest_hour_rec['solar'] += solar_delta
        latest_hour_rec['solar_consumed'] = max(0, latest_hour_rec['solar'] - latest_hour_rec['export'])
        latest_hour_rec['consumed'] = latest_hour_rec['solar_consumed'] + latest_hour_rec['import']
        latest_hour_rec['co2'] = (config['environment']['gco2_kwh'] * latest_hour_rec['solar']) / 1000
        latest_hour_rec['trees'] = config['environment']['trees_kwh'] * latest_hour_rec['solar']

        # apply offsets for today and recalc derived values 
        today_rec = gv_shelly_dict['month'][-1]
        today_rec['import'] += import_delta
        today_rec['export'] += export_delta
        today_rec['solar'] += solar_delta
        today_rec['solar_consumed'] = max(0, today_rec['solar'] - today_rec['export'])
        today_rec['consumed'] = today_rec['solar_consumed'] + today_rec['import']
        today_rec['co2'] = (config['environment']['gco2_kwh'] * today_rec['solar']) / 1000
        today_rec['trees'] = config['environment']['trees_kwh'] * today_rec['solar']

        # apply offsets for this month and recalc derived values 
        this_month_rec = gv_shelly_dict['year'][-1]
        this_month_rec['import'] += import_delta
        this_month_rec['export'] += export_delta
        this_month_rec['solar'] += solar_delta
        this_month_rec['solar_consumed'] = max(0, this_month_rec['solar'] - this_month_rec['export'])
        this_month_rec['consumed'] = this_month_rec['solar_consumed'] + this_month_rec['import']
        this_month_rec['co2'] = (config['environment']['gco2_kwh'] * this_month_rec['solar']) / 1000
        this_month_rec['trees'] = config['environment']['trees_kwh'] * this_month_rec['solar']

        # update cloud data timestamps
        gv_shelly_dict['day_last_updated'] = int(time.time())
        gv_shelly_dict['month_last_updated'] = int(time.time())
        gv_shelly_dict['year_last_updated'] = int(time.time())

    # snapshot the total data for the next delta calculation
    gv_total_snapshot_rec = copy.deepcopy(gv_shelly_dict['total'])

    utils.log_message(
            1,
            'Live import:%.3f kW (+%.5f kWh)' % (
                live_rec['import'],
                import_delta,
                )
            )

    utils.log_message(
            1,
            'Live export:%.3f kW (+%.5f kWh)' % (
                live_rec['export'],
                export_delta,
                )
            )

    utils.log_message(
            1,
            'Live solar:%.3f kW (+%.5f kWh)' % (
                live_rec['solar'],
                solar_delta,
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
    config    - global config

    Returns: tuple of the data dict and refresh interval (fixed at 5 seconds)
    """
    global gv_shelly_dict

    # single-phase shelly-em as inverter or grid source
    # we need the API creds and single device_id
    valid_config = True
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        if (
                not config['shelly']['api_host'] or
                not config['shelly']['auth_key'] or
                not config['shelly']['device_id']
                ):
            utils.log_message(
                    1,
                    'Cloud API creds are not configured for Shelly EM.. skipping'
                    )
            valid_config = False 

    # 3em as inverter in either grid-only, pv-only or both
    # we need the API creds and one of the  device_ids
    if (config['data_source'] == 'shelly-em' or 
        config['grid_source'] == 'shelly-em'):
        if (
                not config['shelly']['api_host'] or
                not config['shelly']['auth_key'] or
                (not config['shelly']['device_id'] and 
                 not config['shelly']['device_id_pv'])
                ):
            utils.log_message(
                    1,
                    'Cloud API creds are not configured for Shelly 3EM.. skipping'
                    )
            valid_config = False 

    if valid_config:
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
