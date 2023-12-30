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
import concurrent.futures
import cherrypy

# global variables
gv_verbose = 0

# global config
gv_config_dict = {}
gv_config_file = '%s/config.json' % (
        os.path.dirname(
            os.path.realpath(__file__)
            )
        )

# tracked device and API data
gv_data_dict = {}
gv_data_dict['last_updated'] = 0

# day, month and year records
gv_data_dict['day'] = []
gv_data_dict['month'] = []
gv_data_dict['year'] = []

# dashboard directives to web page
gv_data_dict['dashboard'] = {}

# metrics
gv_data_dict['metrics'] = {}
gv_data_dict['metrics']['live'] = {}
gv_data_dict['metrics']['live']['import'] = 0
gv_data_dict['metrics']['live']['solar'] = 0
gv_data_dict['metrics']['live']['solar_consumed'] = 0
gv_data_dict['metrics']['live']['export'] = 0
gv_data_dict['metrics']['live']['consumed'] = 0

gv_data_dict['metrics']['today'] = {}
gv_data_dict['metrics']['today']['import'] = 0
gv_data_dict['metrics']['today']['solar'] = 0
gv_data_dict['metrics']['today']['solar_consumed'] = 0
gv_data_dict['metrics']['today']['export'] = 0
gv_data_dict['metrics']['today']['consumed'] = 0

gv_data_dict['metrics']['yesterday'] = {}
gv_data_dict['metrics']['yesterday']['import'] = 0
gv_data_dict['metrics']['yesterday']['solar'] = 0
gv_data_dict['metrics']['yesterday']['solar_consumed'] = 0
gv_data_dict['metrics']['yesterday']['export'] = 0
gv_data_dict['metrics']['yesterday']['consumed'] = 0

gv_data_dict['metrics']['this_month'] = {}
gv_data_dict['metrics']['this_month']['import'] = 0
gv_data_dict['metrics']['this_month']['solar'] = 0
gv_data_dict['metrics']['this_month']['solar_consumed'] = 0
gv_data_dict['metrics']['this_month']['export'] = 0
gv_data_dict['metrics']['this_month']['consumed'] = 0

gv_data_dict['metrics']['last_month'] = {}
gv_data_dict['metrics']['last_month']['import'] = 0
gv_data_dict['metrics']['last_month']['solar'] = 0
gv_data_dict['metrics']['last_month']['solar_consumed'] = 0
gv_data_dict['metrics']['last_month']['export'] = 0
gv_data_dict['metrics']['last_month']['consumed'] = 0

gv_data_dict['metrics']['this_year'] = {}
gv_data_dict['metrics']['this_year']['import'] = 0
gv_data_dict['metrics']['this_year']['solar'] = 0
gv_data_dict['metrics']['this_year']['solar_consumed'] = 0
gv_data_dict['metrics']['this_year']['export'] = 0
gv_data_dict['metrics']['this_year']['consumed'] = 0


def log_message(
        verbose,
        message):

    if verbose:
        print(
                '%s %s' % (
                    time.asctime(), 
                    message
                    )
                )
        sys.stdout.flush()

    return


def get_last_updated_time():
    # epoch msecs
    return int(time.time() * 1000)


def set_default_config():

    log_message(
            1,
            "Setting config defaults")
    json_config = {}

    # web and default admin user
    json_config['web'] = {}
    json_config['web']['port'] = 8090
    json_config['web']['users'] = {}
    json_config['web']['users']['admin'] = '123456789'

    # logging
    json_config['logging'] = {}
    json_config['logging']['enabled'] = False
    json_config['logging']['verbose'] = False
    json_config['logging']['file'] = ""

    # simulation
    json_config['simulation'] = {}
    json_config['simulation']['fake_live_data'] = False

    # shelly
    json_config['shelly'] = {}
    json_config['shelly']['api_host'] = ''
    json_config['shelly']['auth_key'] = ''
    json_config['shelly']['device_id'] = ''
    json_config['shelly']['device_host'] = ''
    json_config['shelly']['device_username'] = 'none'
    json_config['shelly']['device_password'] = 'none'

    # dashboard
    json_config['dashboard'] = {}

    json_config['dashboard']['donut'] = {}
    json_config['dashboard']['donut']['consumed'] = False
    json_config['dashboard']['donut']['export'] = True
    json_config['dashboard']['donut']['import'] = True
    json_config['dashboard']['donut']['solar'] = False
    json_config['dashboard']['donut']['solar_consumed'] = True

    json_config['dashboard']['bar_chart'] = {}
    json_config['dashboard']['bar_chart']['consumed'] = False
    json_config['dashboard']['bar_chart']['export'] = True
    json_config['dashboard']['bar_chart']['import'] = True
    json_config['dashboard']['bar_chart']['solar'] = True
    json_config['dashboard']['bar_chart']['solar_consumed'] = True

    return json_config


def load_config(config_file):

    log_message(
            1,
            "Loading config from %s" % (config_file))
    try:
        config_data = open(config_file).read()
        json_config = json.loads(config_data)

    except Exception as ex: 
        log_message(
                1,
                "load config failed: %s" % (ex))
        json_config = None

    return json_config


def save_config(json_config, config_file):
    log_message(
            1,
            "Saving config to %s" % (config_file))
    with open(gv_config_file, 'w') as outfile:
        indented_json_str = json.dumps(json_config, 
                                       indent=4, 
                                       sort_keys=True)
        outfile.write(indented_json_str)
        outfile.close()


def config_agent():
    global gv_config_dict
    global gv_config_file
    global gv_verbose
    last_check = 0

    # Default config in case it does not exist
    if (not os.path.isfile(gv_config_file)):
        gv_config_dict = set_default_config()
        save_config(gv_config_dict, gv_config_file)

    # 10-second check for config changes
    while (1):
        config_last_modified = os.path.getmtime(gv_config_file)

        if config_last_modified > last_check:
            json_config = load_config(gv_config_file)
            if json_config: 
                gv_config_dict = json_config
                last_check = config_last_modified
                gv_verbose = gv_config_dict['logging']['verbose']
                gv_data_dict['dashboard'] = gv_config_dict['dashboard']

        time.sleep(10)


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
        api_host,
        auth_key,
        device_id,
        date_range,
        date_from,
        date_to):

    global gv_verbose

    # check if creds are set
    if (
            not api_host or
            not auth_key or
            not device_id
            ):
        log_message(
                1,
                "Cloud API creds are not configured.. skipping"
                )
        return None

    # API URL and params
    shelly_cloud_url = 'https://%s/v2/statistics/power-consumption/em-1p' % (
            api_host)
    params = {}
    params['id'] = device_id
    params['auth_key'] = auth_key
    params['date_range'] = date_range

    if date_from:
        params['date_from'] = date_from

    if date_to:
        params['date_to'] = date_to

    # channel 0 (grid consumption and return)
    params['channel'] = 0
    try:
        log_message(
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
        log_message(
                1,
                'Shelly Cloud API Call to %s, params %s failed' % (
                    shelly_cloud_url,
                    params
                    )
                )
        return None

    log_message(
            gv_verbose,
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
        log_message(
                1,
                'Shelly Cloud API Call to %s, params %s failed' % (
                    shelly_cloud_url,
                    params
                    )
                )
        return None


    log_message(
            gv_verbose,
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
            usage_rec['day'] = '%d' % (
                    ts_dt.day)
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

    # reformat to list of records
    data_list = []
    for key in sorted(data_dict.keys()):
        data_list.append(data_dict[key])

    return data_list


def cloud_api_agent():

    global gv_data_dict
    global gv_config_dict
    global gv_verbose

    log_message(
            1,
            "Cloud API Agent started"
            )

    # timestamps to track the next call
    month_ts = 0
    year_ts = 0
    day_ts = 0

    # initial sleep is 0 
    # and will be 60s thereafter
    sleep_interval = 0

    while True:
        time.sleep(sleep_interval)
        sleep_interval = 60

        log_message(
                1,
                'Cloud API Refresh timestamps.. day:%d month:%d year:%d' % (
                    day_ts,
                    month_ts,
                    year_ts)
                )

        now = int(time.time())
        dt_today = datetime.datetime.today() 

        if now >= day_ts:
            # last 36
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
                    api_host = gv_config_dict['shelly']['api_host'],
                    auth_key = gv_config_dict['shelly']['auth_key'],
                    device_id = gv_config_dict['shelly']['device_id'],
                    date_range = 'custom',
                    date_from = day_ago_str,
                    date_to = day_end_str)
            
            if day_data:
                # reset timestamp
                # for :10 past next hour
                day_ts = ((70 - dt_today.minute) * 60) + now

                log_message(
                        gv_verbose,
                        'last 24h API Data\n%s\n' % (
                            json.dumps(
                                day_data, 
                                indent = 4),
                            )
                        )
                gv_data_dict['day'] = day_data
                gv_data_dict['last_updated'] = get_last_updated_time()
        
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
                    api_host = gv_config_dict['shelly']['api_host'],
                    auth_key = gv_config_dict['shelly']['auth_key'],
                    device_id = gv_config_dict['shelly']['device_id'],
                    date_range = 'custom',
                    date_from = month_start_str,
                    date_to = month_end_str)
            
            if month_data:
                # reset timestamp
                # for :10 past next hour
                month_ts = ((70 - dt_today.minute) * 60) + now
                log_message(
                        gv_verbose,
                        'Month API Data\n%s\n' % (
                            json.dumps(
                                month_data, 
                                indent = 4),
                            )
                        )
                gv_data_dict['month'] = month_data
                gv_data_dict['last_updated'] = get_last_updated_time()

                # take todays totals from last recorded day in month
                today_rec = month_data[-1]
                gv_data_dict['metrics']['today']['import'] = today_rec['import']
                gv_data_dict['metrics']['today']['solar'] = today_rec['solar']
                gv_data_dict['metrics']['today']['solar_consumed'] = today_rec['solar_consumed']
                gv_data_dict['metrics']['today']['export'] = today_rec['export']
                gv_data_dict['metrics']['today']['consumed'] = today_rec['import'] +  today_rec['solar_consumed']

                if len(month_data) >= 2:
                    yesterday_rec = month_data[-2]
                    gv_data_dict['metrics']['yesterday']['import'] = yesterday_rec['import']
                    gv_data_dict['metrics']['yesterday']['solar'] = yesterday_rec['solar']
                    gv_data_dict['metrics']['yesterday']['solar_consumed'] = yesterday_rec['solar_consumed']
                    gv_data_dict['metrics']['yesterday']['export'] = yesterday_rec['export']
                    gv_data_dict['metrics']['yesterday']['consumed'] = yesterday_rec['import'] + yesterday_rec['solar_consumed']

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
                    api_host = gv_config_dict['shelly']['api_host'],
                    auth_key = gv_config_dict['shelly']['auth_key'],
                    device_id = gv_config_dict['shelly']['device_id'],
                    date_range = 'custom',
                    date_from = last_year_start_str,
                    date_to = year_end_str)
            
            if year_data:
                # reset timestamp
                # for :10 past next hour
                year_ts = ((70 - dt_today.minute) * 60) + now
                log_message(
                        gv_verbose,
                        'Year API Data\n%s\n' % (
                            json.dumps(
                                year_data, 
                                indent = 4),
                            )
                        )
                gv_data_dict['year'] = year_data
                gv_data_dict['last_updated'] = get_last_updated_time()

                # take months totals from last recorded month in year
                month_rec = year_data[-1]
                gv_data_dict['metrics']['this_month']['import'] = month_rec['import']
                gv_data_dict['metrics']['this_month']['solar'] = month_rec['solar']
                gv_data_dict['metrics']['this_month']['solar_consumed'] = month_rec['solar_consumed']
                gv_data_dict['metrics']['this_month']['export'] = month_rec['export']
                gv_data_dict['metrics']['this_month']['consumed'] = month_rec['import'] + month_rec['solar_consumed']

                if len(year_data) >= 2:
                    last_month_rec = year_data[-2]
                    gv_data_dict['metrics']['last_month']['import'] = last_month_rec['import']
                    gv_data_dict['metrics']['last_month']['solar'] = last_month_rec['solar']
                    gv_data_dict['metrics']['last_month']['solar_consumed'] = last_month_rec['solar_consumed']
                    gv_data_dict['metrics']['last_month']['export'] = last_month_rec['export']
                    gv_data_dict['metrics']['last_month']['consumed'] = last_month_rec['import'] + last_month_rec['solar_consumed']

                # this year
                # add all month records for last referenced year
                this_year = month_rec['year']

                # reset
                gv_data_dict['metrics']['this_year']['import'] = 0
                gv_data_dict['metrics']['this_year']['solar'] = 0
                gv_data_dict['metrics']['this_year']['solar_consumed'] = 0
                gv_data_dict['metrics']['this_year']['export'] = 0
                gv_data_dict['metrics']['this_year']['consumed'] = 0

                for month_rec in year_data:
                    if month_rec['year'] != this_year:
                        continue

                    gv_data_dict['metrics']['this_year']['import'] += month_rec['import']
                    gv_data_dict['metrics']['this_year']['solar'] += month_rec['solar']
                    gv_data_dict['metrics']['this_year']['solar_consumed'] += month_rec['solar_consumed']
                    gv_data_dict['metrics']['this_year']['export'] += month_rec['export']
                    gv_data_dict['metrics']['this_year']['consumed'] += month_rec['import'] + month_rec['solar_consumed']


    return


def device_api_agent():

    global gv_verbose
    global gv_data_dict
    global gv_config_dict

    log_message(
            1,
            "Device API Agent started"
            )

    # initial sleep is 0 
    # and will be 5s thereafter
    sleep_interval = 0

    while True:
        time.sleep(sleep_interval)
        sleep_interval = 5

        device_url = 'http://%s/status' % (gv_config_dict['shelly']['device_host'])
        basic =  requests.auth.HTTPBasicAuth(
                gv_config_dict['shelly']['device_username'], 
                gv_config_dict['shelly']['device_password']) 

        if not gv_config_dict['shelly']['device_host']:
            log_message(
                    1,
                    "Device Host is not configured.. skipping "
                    )
            continue

        try:
            log_message(
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
            log_message(
                    1,
                    'Shelly Device API Call to %s failed' % (
                        device_url,
                        )
                    )
            continue

        log_message(
                gv_verbose,
                'Device API Response\n%s\n' % (
                    json.dumps(device_resp_dict, indent = 4),
                    )
                )

        # convert to kWh
        grid = device_resp_dict['emeters'][0]['power'] / 1000
        solar = device_resp_dict['emeters'][1]['power'] / 1000

        # fake over-rides
        if gv_config_dict['simulation']['fake_live_data']:
            solar = random.randint(0, 12) 
            if solar > 0:
                solar += 0.555 # cheap tell-tail for fake
            grid = 0
            if solar >= 4:
                # export
                grid = random.randint(int(solar * 0.7) * -1, 4) + 0.555
            else:
                # import
                grid = random.randint(0, 4) + 0.555

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

        log_message(
                1,
                "Shelly Device: import:%f export:%f solar:%f consumed:%f" % (
                    gv_data_dict['metrics']['live']['import'],
                    gv_data_dict['metrics']['live']['export'],
                    gv_data_dict['metrics']['live']['solar'],
                    gv_data_dict['metrics']['live']['consumed'],
                    )
                )
        gv_data_dict['last_updated'] = get_last_updated_time()

    return


def build_dash_web_page():
    global gv_verbose
    global gv_data_dict

    log_message(
            gv_verbose,
            'Building /dashboard webpage')

    dash_filename = '%s/dash.html' % (
            os.path.dirname(os.path.realpath(__file__))
            )

    # read file in 
    dash_file = open(dash_filename, "r")
    dash_page_str = dash_file.read()
    dash_file.close()

    return dash_page_str


class dash_handler(object):
    @cherrypy.expose()

    def index(
            self):

        global gv_verbose

        log_message(
                gv_verbose,
                '/ (%s)' % (
                    cherrypy.request.params)
                )

        return build_dash_web_page()

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


def build_admin_web_page():
    global gv_verbose
    global gv_data_dict
    global gv_config_dict

    log_message(
            1,
            '/admin page %s params:%s' % (
                cherrypy.request.remote.ip,
                cherrypy.request.params))

    admin_filename = '%s/admin.html' % (
            os.path.dirname(os.path.realpath(__file__))
            )

    # read file in 
    admin_file = open(admin_filename, "r")
    admin_page_str = admin_file.read()
    admin_file.close()

    # substitute in existing values
    admin_page_str = admin_page_str.replace(
            '__shelly_api_host__', 
            gv_config_dict['shelly']['api_host'])

    admin_page_str = admin_page_str.replace(
            '__shelly_auth_key__', 
            gv_config_dict['shelly']['auth_key'])

    admin_page_str = admin_page_str.replace(
            '__shelly_device_id__', 
            gv_config_dict['shelly']['device_id'])

    admin_page_str = admin_page_str.replace(
            '__shelly_device_host__', 
            gv_config_dict['shelly']['device_host'])

    admin_page_str = admin_page_str.replace(
            '__shelly_device_username__', 
            gv_config_dict['shelly']['device_username'])

    admin_page_str = admin_page_str.replace(
            '__shelly_device_password__', 
            gv_config_dict['shelly']['device_password'])

    admin_page_str = admin_page_str.replace(
            '__donut_import_checked__', 
            'checked' if gv_config_dict['dashboard']['donut']['import'] else '')

    admin_page_str = admin_page_str.replace(
            '__donut_consumed_checked__', 
            'checked' if gv_config_dict['dashboard']['donut']['consumed'] else '')

    admin_page_str = admin_page_str.replace(
            '__donut_solar_checked__', 
            'checked' if gv_config_dict['dashboard']['donut']['solar'] else '')

    admin_page_str = admin_page_str.replace(
            '__donut_solar_consumed_checked__', 
            'checked' if gv_config_dict['dashboard']['donut']['solar_consumed'] else '')

    admin_page_str = admin_page_str.replace(
            '__donut_export_checked__', 
            'checked' if gv_config_dict['dashboard']['donut']['export'] else '')

    admin_page_str = admin_page_str.replace(
            '__bar_chart_import_checked__', 
            'checked' if gv_config_dict['dashboard']['bar_chart']['import'] else '')

    admin_page_str = admin_page_str.replace(
            '__bar_chart_consumed_checked__', 
            'checked' if gv_config_dict['dashboard']['bar_chart']['consumed'] else '')

    admin_page_str = admin_page_str.replace(
            '__bar_chart_solar_checked__', 
            'checked' if gv_config_dict['dashboard']['bar_chart']['solar'] else '')

    admin_page_str = admin_page_str.replace(
            '__bar_chart_solar_consumed_checked__', 
            'checked' if gv_config_dict['dashboard']['bar_chart']['solar_consumed'] else '')

    admin_page_str = admin_page_str.replace(
            '__bar_chart_export_checked__', 
            'checked' if gv_config_dict['dashboard']['bar_chart']['export'] else '')

    admin_page_str = admin_page_str.replace(
            '__logging_checked__', 
            'checked' if gv_config_dict['logging']['enabled'] else '')

    admin_page_str = admin_page_str.replace(
            '__verbose_logging_checked__', 
            'checked' if gv_config_dict['logging']['verbose'] else '')

    admin_page_str = admin_page_str.replace(
            '__fake_live_data_checked__', 
            'checked' if gv_config_dict['simulation']['fake_live_data'] else '')

    return admin_page_str


class admin_handler(object):
    @cherrypy.expose()

    def index(
            self,
            shelly_api_host = None,
            shelly_auth_key = None,
            shelly_device_id = None,
            shelly_device_host = None,
            shelly_device_username = None,
            shelly_device_password = None,
            donut_import = None,
            donut_consumed = None,
            donut_solar = None,
            donut_solar_consumed = None,
            donut_export = None,
            bar_chart_import = None,
            bar_chart_consumed = None,
            bar_chart_solar = None,
            bar_chart_solar_consumed = None,
            bar_chart_export = None,
            logging = None,
            verbose_logging = None,
            fake_live_data = None,
            ):

        global gv_verbose
        global gv_config_dict
        global gv_config_file

        log_message(
                gv_verbose,
                '/admin (%s) params:%s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.params)
                )

        if len(cherrypy.request.params) > 0:
            # apply config updates
            if shelly_api_host:
                gv_config_dict['shelly']['api_host'] = shelly_api_host

            if shelly_auth_key:
                gv_config_dict['shelly']['auth_key'] = shelly_auth_key

            if shelly_device_id:
                gv_config_dict['shelly']['device_id'] = shelly_device_id

            if shelly_device_host:
                gv_config_dict['shelly']['device_host'] = shelly_device_host

            if shelly_device_username:
                gv_config_dict['shelly']['device_username'] = shelly_device_username

            if shelly_device_password:
                gv_config_dict['shelly']['device_password'] = shelly_device_password

            # donut chart
            gv_config_dict['dashboard']['donut']['import'] = True if donut_import else False
            gv_config_dict['dashboard']['donut']['consumed'] = True if donut_consumed else False
            gv_config_dict['dashboard']['donut']['solar'] = True if donut_solar else False
            gv_config_dict['dashboard']['donut']['solar_consumed'] = True if donut_solar_consumed else False
            gv_config_dict['dashboard']['donut']['export'] = True if donut_export else False

            # bar chart
            gv_config_dict['dashboard']['bar_chart']['import'] = True if bar_chart_import else False
            gv_config_dict['dashboard']['bar_chart']['consumed'] = True if bar_chart_consumed else False
            gv_config_dict['dashboard']['bar_chart']['solar'] = True if bar_chart_solar else False
            gv_config_dict['dashboard']['bar_chart']['solar_consumed'] = True if bar_chart_solar_consumed else False
            gv_config_dict['dashboard']['bar_chart']['export'] = True if bar_chart_export else False

            # logging and faking
            gv_config_dict['logging']['enabled'] = True if logging else False
            gv_config_dict['logging']['verbose'] = True if verbose_logging else False
            gv_config_dict['simulation']['fake_live_data'] = True if fake_live_data else False

            save_config(gv_config_dict, gv_config_file)


        return build_admin_web_page()

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


class api_handler(object):
    @cherrypy.expose()
    @cherrypy.tools.json_out()

    def index(
            self):

        global gv_verbose

        log_message(
                gv_verbose,
                '/dash API %s params:%s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.params))

        return json.dumps(gv_data_dict, indent = 4)

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


def web_server(dev_mode):
    global gv_config_dict

    log_message(
            1,
            'Starting web server.. dev_mode:%s' % (
                dev_mode)
            )

    # engine config for production
    # lockds down exception logging from web I/F
    if not dev_mode:
        cherrypy.config.update(
                {
                    'environment': 'production',
                    'log.screen': False,
                    'log.access_file': '',
                    'log.error_file': ''
                    }
                )

    # Listen on our port on any IF
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = gv_config_dict['web']['port']

    # /images (for favicon)
    images_dir = '%s/images' % (
            os.path.dirname(os.path.realpath(__file__))
            )

    # / dashboard
    dash_conf = {
            '/favicon.png':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': '%s/favicon.png' % (images_dir)
                }
            }
    cherrypy.tree.mount(dash_handler(), '/', dash_conf)

    # /data dashboard
    api_conf = {}
    cherrypy.tree.mount(api_handler(), '/data', api_conf)

    # /admin admin
    admin_conf = {}
    users = gv_config_dict['web']['users']
    if len(users) > 0:
        ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(users)

        # Generate a random digest auth key
        # Might help against is getting compromised
        random.seed()
        digest_key = hex(random.randint(0x1000000000000000,
                                        0xFFFFFFFFFFFFFFFF))
        digest_conf = {
                'tools.auth_digest.on': True,
                'tools.auth_digest.realm': 'localhost',
                'tools.auth_digest.get_ha1': ha1,
                'tools.auth_digest.key': digest_key,
        }

        admin_conf = {
            '/': digest_conf
        }
    cherrypy.tree.mount(admin_handler(), '/admin', admin_conf)

    # Cherrypy main loop blocking
    cherrypy.engine.start()
    cherrypy.engine.block()

    return


def thread_exception_wrapper(
        fn, 
        *args, 
        **kwargs):

    try:
        # call fn arg with other args
        return fn(*args, **kwargs)

    except Exception:
        # generate a formal backtrace as a string
        # and raise this as a new exception with that string as title
        exception_detail = sys.exc_info()
        exception_list = traceback.format_exception(
                *exception_detail,
                limit = 200)
        exception_str = ''.join(exception_list)

        raise Exception(exception_str)  

# main()
parser = argparse.ArgumentParser(
        description = 'Solar Monitor'
        )

parser.add_argument(
        '--dev', 
        help = 'Enable Development mode', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
dev_mode = args['dev']

# Thread management 
executor = concurrent.futures.ThreadPoolExecutor(
        max_workers = 20)
future_dict = {}

# Config Agent
future_dict['Config Agent'] = executor.submit(
        thread_exception_wrapper,
        config_agent)

# allow config to init
time.sleep(5)

# Cloud API Agent
future_dict['Cloud API Agent'] = executor.submit(
        thread_exception_wrapper,
        cloud_api_agent
        )

# Device API Agent
future_dict['Device API Agent'] = executor.submit(
        thread_exception_wrapper,
        device_api_agent
        )

# Cherry Py web server
future_dict['Web Server'] = executor.submit(
        thread_exception_wrapper,
        web_server,
        dev_mode)

# main loop
while (True):
    exception_dict = {}
    log_message(
            gv_verbose, 
            'threads:%s' % (
                future_dict)
            )

    for key in future_dict:
        future = future_dict[key]
        if future.done():
            if future.exception():
                exception_dict[key] = future.exception()

    if (len(exception_dict) > 0):
        log_message(
                1,
                'Exceptions Detected:\n%s' % (
                    exception_dict)
                )
        os._exit(1) 
        
    time.sleep(5)
