import argparse
import requests
import json
import os
import sys
import traceback
import time
import datetime
import zoneinfo
import random
import concurrent.futures
import cherrypy
import utils
import shelly
import solis

# global config
gv_config_dict = {}
gv_config_file = '%s/config.json' % (
        os.path.dirname(
            os.path.realpath(__file__)
            )
        )

gv_root = '%s' % (
        os.path.dirname(
            os.path.realpath(__file__)
            )
        )

# tracked device and API data
gv_data_dict = {}
gv_data_dict['last_updated'] = 0

gv_refresh_interval = 1

def set_default_config():

    utils.log_message(
            1,
            "Setting config defaults")
    json_config = {}

    # web and default admin user
    json_config['web'] = {}
    json_config['web']['port'] = 8090
    json_config['web']['users'] = {}
    json_config['web']['users']['admin'] = '123456789'

    # data source
    json_config['data_source'] = "none"

    # dashboard
    json_config['dashboard'] = {}

    json_config['dashboard']['cycle_interval'] = 10

    json_config['dashboard']['metrics'] = {}
    json_config['dashboard']['metrics']['live'] = True
    json_config['dashboard']['metrics']['today'] = True
    json_config['dashboard']['metrics']['yesterday'] = True
    json_config['dashboard']['metrics']['this_month'] = True
    json_config['dashboard']['metrics']['last_month'] = True
    json_config['dashboard']['metrics']['last_12_months'] = True

    json_config['dashboard']['donut'] = {}
    json_config['dashboard']['donut']['consumed'] = False
    json_config['dashboard']['donut']['export'] = False
    json_config['dashboard']['donut']['import'] = True
    json_config['dashboard']['donut']['solar'] = False
    json_config['dashboard']['donut']['solar_consumed'] = True

    json_config['dashboard']['bar_chart'] = {}
    json_config['dashboard']['bar_chart']['consumed'] = False
    json_config['dashboard']['bar_chart']['export'] = True
    json_config['dashboard']['bar_chart']['import'] = True
    json_config['dashboard']['bar_chart']['solar'] = True
    json_config['dashboard']['bar_chart']['solar_consumed'] = True

    json_config['environment'] = {}
    json_config['environment']['gco2_kwh'] = 297.4
    json_config['environment']['trees_kwh'] = 0.0117

    return json_config


def load_config(config_file):

    utils.log_message(
            1,
            "Loading config from %s" % (config_file))
    try:
        config_data = open(config_file).read()
        json_config = json.loads(config_data)

    except Exception as ex: 
        utils.log_message(
                1,
                "load config failed: %s" % (ex))
        json_config = None

    return json_config


def save_config(json_config, config_file):
    utils.log_message(
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

        time.sleep(10)


def monitor_agent():

    global gv_data_dict
    global gv_config_dict
    global gv_force_refresh
    global gv_dev_mode
    global gv_force_metric_cycle
    global gv_refresh_interval

    utils.log_message(
            1,
            "Monitor API Agent started"
            )

    sleep_interval = 5

    while True:
        if gv_config_dict['data_source'] == 'shelly-em':
            gv_data_dict, sleep_interval = shelly.get_data(gv_config_dict)
        elif gv_config_dict['data_source'] == 'solis':
            gv_data_dict, sleep_interval = solis.get_data(gv_config_dict)
        else:
            utils.log_message(
                    1,
                    "No data source is configured"
                    )

        # FIXME elseif others into place

        # short sleep protection
        if sleep_interval < 5:
            sleep_interval = 5

        # refresh interval
        # we want a min of 10 but can go 
        # lower for more real-time values
        gv_refresh_interval = min(10, sleep_interval)

        utils.log_message(
                1,
                "Monitor sleeping for %d seconds" % (sleep_interval)
                )
        time.sleep(sleep_interval)

    return


class config_handler(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()

    def index(self):

        global gv_config_dict
        global gv_config_file

        utils.log_message(
                utils.gv_verbose,
                '/config API %s %s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.method))

        if cherrypy.request.method == 'GET':
            # retrieve config
            return json.dumps(gv_config_dict, indent = 4)

        if cherrypy.request.method == 'POST':
            # update config
            updated_config_dict = json.loads(cherrypy.request.body.read())
            utils.log_message(
                    utils.gv_verbose,
                    'config post %s' % (updated_config_dict)
                    )

            # map like to like keys in config
            # this is a hack as its allowing config to exist that is not 
            # served back from the admin page
            # users and ports are examples of fields like this
            for key in updated_config_dict:
                gv_config_dict[key] = updated_config_dict[key]

            save_config(gv_config_dict, gv_config_file)
            return ""

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


class data_handler(object):
    @cherrypy.expose()
    @cherrypy.tools.json_out()

    def index(self):
        global gv_data_dict
        global gv_config_dict
        global gv_refresh_interval
        global gv_force_refresh
        global gv_force_metric_cycle

        utils.log_message(
                utils.gv_verbose,
                '/data API %s %s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.method))

        # merge in config for dashboard
        gv_data_dict['dashboard'] = gv_config_dict['dashboard']

        # run-time over-ride of refresh (not really a config option)
        gv_data_dict['dashboard']['refresh_interval'] = gv_refresh_interval

        # dev mode override for refresh
        if (gv_dev_mode and gv_force_refresh):
            gv_data_dict['dashboard']['refresh_interval'] = gv_force_refresh

        # dev mode override for metric cycle
        if (gv_dev_mode and gv_force_metric_cycle):
            gv_data_dict['dashboard']['cycle_interval'] = gv_force_metric_cycle 

        return json.dumps(gv_data_dict, indent = 4)

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


def web_server(dev_mode):
    global gv_config_dict

    utils.log_message(
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

    # static hosting of www dir on /
    # with default index being dash.html
    www_dir = '%s/www' % (
            os.path.dirname(os.path.realpath(__file__))
            )

    static_conf = {
            '/':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': www_dir,
                'tools.staticdir.index': 'dash.html',
                }
            }
    cherrypy.tree.mount(None, '/', static_conf)

    # /data API
    api_conf = {}
    cherrypy.tree.mount(data_handler(), '/data', api_conf)

    # /admin (for config page)
    users = gv_config_dict['web']['users']
    ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(users)

    # Generate a random digest auth key
    random.seed()
    digest_key = hex(random.randint(0x1000000000000000,
                                    0xFFFFFFFFFFFFFFFF))
    admin_conf = {
            '/': {
                'tools.auth_digest.on': True,
                'tools.auth_digest.realm': 'localhost',
                'tools.auth_digest.get_ha1': ha1,
                'tools.auth_digest.key': digest_key,

                'tools.staticdir.on': True,
                'tools.staticdir.dir': www_dir,
                'tools.staticdir.index': 'admin.html',
                }

            }    
    cherrypy.tree.mount(None, '/admin', admin_conf)

    # /config (API for reading/writing config)
    # authenticated the same as /admin
    config_conf = {
            '/': {
                'tools.auth_digest.on': True,
                'tools.auth_digest.realm': 'localhost',
                'tools.auth_digest.get_ha1': ha1,
                'tools.auth_digest.key': digest_key,
                }
            }
    cherrypy.tree.mount(config_handler(), '/config', config_conf)

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

parser.add_argument(
        '--config', 
        help = 'Config File Location (defaults to same dir as script)', 
        required = False,
        default = gv_config_file
        )

parser.add_argument(
        '--force_refresh', 
        help = 'Forced Refresh Interval (dev feature only)', 
        type = int,
        default = 0,
        required = False
        )

parser.add_argument(
        '--force_metric_cycle', 
        help = 'Forced Metric Cycle Interval (dev feature only)', 
        type = int,
        default = 0,
        required = False
        )

parser.add_argument(
        '--verbose', 
        help = 'Verbose Logging', 
        action = 'store_true'
        )


args = vars(parser.parse_args())
gv_dev_mode = args['dev']
gv_config_file = args['config']
gv_force_refresh = args['force_refresh']
gv_force_metric_cycle = args['force_metric_cycle']
utils.gv_verbose = args['verbose']

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

# Monitor API Agent
future_dict['Monitor API Agent'] = executor.submit(
        thread_exception_wrapper,
        monitor_agent
        )

# Cherry Py web server
future_dict['Web Server'] = executor.submit(
        thread_exception_wrapper,
        web_server,
        gv_dev_mode)

# main loop
while (True):
    exception_dict = {}
    utils.log_message(
            utils.gv_verbose, 
            'threads:%s' % (
                future_dict)
            )

    for key in future_dict:
        future = future_dict[key]
        if future.done():
            if future.exception():
                exception_dict[key] = future.exception()

    if (len(exception_dict) > 0):
        utils.log_message(
                1,
                '%d Exceptions Detected' % (len(exception_dict))
                )
        for key in exception_dict:
            utils.log_message(
                    1,
                    'Exceptions in %s:\n%s\n' % (
                        key,
                        exception_dict[key])
                    )
        os._exit(1) 
        
    time.sleep(5)
