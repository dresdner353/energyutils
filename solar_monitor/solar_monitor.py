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

    utils.log_message(
            1,
            "Monitor API Agent started"
            )

    sleep_interval = 5

    while True:
        if gv_config_dict['data_source'] == 'shelly':
            gv_data_dict, sleep_interval = shelly.get_data(gv_config_dict['shelly'])
        else:
            utils.log_message(
                    1,
                    "No data source is configured"
                    )

        # FIXME elseif others into place

        utils.log_message(
                utils.gv_verbose,
                "Monitor sleeping for %d seconds" % (sleep_interval)
                )
        time.sleep(sleep_interval)

    return


def serve_dash_web_page():
    global gv_data_dict

    utils.log_message(
            utils.gv_verbose,
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

        utils.log_message(
                utils.gv_verbose,
                '/ (%s)' % (
                    cherrypy.request.params)
                )

        return serve_dash_web_page()

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


def serve_admin_web_page():
    global gv_data_dict
    global gv_config_dict

    utils.log_message(
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

    # seed the config into place as a JSON
    # string
    admin_page_str = admin_page_str.replace(
            '__init_config__', 
            json.dumps(gv_config_dict))

    return admin_page_str


class admin_handler(object):
    @cherrypy.expose()

    def index(self):

        utils.log_message(
                utils.gv_verbose,
                '/admin (%s) params:%s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.params)
                )

        return serve_admin_web_page()

    # Force trailling slash off on called URL
    index._cp_config = {'tools.trailing_slash.on': False}


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

        utils.log_message(
                utils.gv_verbose,
                '/data API %s params:%s' % (
                    cherrypy.request.remote.ip,
                    cherrypy.request.params))

        # merge in config for dashboard
        gv_data_dict['dashboard'] = gv_config_dict['dashboard']

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

    # /images (for favicon)
    images_dir = '%s/images' % (
            os.path.dirname(os.path.realpath(__file__))
            )

    # / (dashboard)
    dash_conf = {
            '/favicon.png':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': '%s/favicon.png' % (images_dir)
                }
            }
    cherrypy.tree.mount(dash_handler(), '/', dash_conf)

    # /data API
    api_conf = {}
    cherrypy.tree.mount(data_handler(), '/data', api_conf)

    # /admin (for config page)
    # /config (API for reading/writing config)
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
    cherrypy.tree.mount(config_handler(), '/config', admin_conf)

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
        '--verbose', 
        help = 'Verbose Logging', 
        action = 'store_true'
        )


args = vars(parser.parse_args())
dev_mode = args['dev']
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
        dev_mode)

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
