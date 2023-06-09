import argparse
import requests
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import csv


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

    return


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


def output_results(
        odir,
        output_format,
        data_dict,
        prefix,
        decimal_places):

    # no date, nothing to do
    if len(data_dict) == 0:
        return

    if output_format in ['json', 'both']:
        # JSONL File
        dest_jsonl_file = '%s/%s.jsonl' % (odir, prefix)
        log_message(
                1,
                'Writing to %s' % (
                    dest_jsonl_file)
                )
        with open(dest_jsonl_file, 'w') as f:
            for key in sorted(data_dict.keys()):
                f.write(json.dumps(data_dict[key]) + '\n')

    if output_format in ['csv', 'both']:
        # CSV File
        first_key = list(data_dict.keys())[0]
        first_rec = data_dict[first_key]
        field_list = list(first_rec.keys())
        field_list.sort()
        dest_csv_file = '%s/%s.csv' % (odir, prefix)
        log_message(
                1,
                'Writing to %s' % (
                    dest_csv_file)
                )
        with open(dest_csv_file, 'w') as f:
            writer = csv.DictWriter(
                    f, 
                    fieldnames = field_list)
            writer.writeheader()

            for key in sorted(data_dict.keys()):
                data_rec = data_dict[key]
                for field in data_rec:
                    if type(data_rec[field]) == float:
                        data_rec[field] = round(data_rec[field], decimal_places)
                writer.writerow(data_rec)

    return


# main()

# default storage dir for data
home = os.path.expanduser('~')
default_odir = home + '/.shellyemdata'   

parser = argparse.ArgumentParser(
        description = 'Shelly EM Data Retrieval Utility'
        )

parser.add_argument(
        '--host', 
        help = 'Shelly API Host', 
        required = True
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory for generated files', 
        default = default_odir,
        required = False
        )

parser.add_argument(
        '--format', 
        help = 'Output Format', 
        required = False,
        choices = [
            'json', 
            'csv', 
            'both'
            ],
        default = 'json'
        )

parser.add_argument(
        '--days', 
        help = 'Backfill in days (def 30)', 
        type = int,
        default = 30,
        required = False
        )

parser.add_argument(
        '--id', 
        help = 'Device ID', 
        required = True
        )

parser.add_argument(
        '--auth_key', 
        help = 'API Auth Key', 
        required = True
        )

parser.add_argument(
        '--force_download', 
        help = 'Force download data (even if already present)', 
        action = 'store_true'
        )

parser.add_argument(
        '--incl_today', 
        help = 'Request data for current incomplete day and all of yesterday', 
        action = 'store_true'
        )

parser.add_argument(
        '--decimal_places', 
        help = 'Decimal Places (def:3)', 
        type = int,
        default = 3,
        required = False
        )

parser.add_argument(
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
api_host = args['host']
backfill_days = args['days']
odir = args['odir']
output_format = args['format']
device_id = args['id']
auth_key = args['auth_key']
incl_today = args['incl_today']
force_download = args['force_download']
decimal_places = args['decimal_places']
gv_verbose = args['verbose']

# JSON encoder force decimal places to 3
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

if not os.path.exists(odir):
    os.mkdir(odir)

# API URL and params
shelly_cloud_url = 'https://%s/statistics/emeter/consumption' % (api_host)
params = {}
params['id'] = device_id
params['auth_key'] = auth_key
params['date_range'] = 'day'

# date reference for retrieval
today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days = 1)

# Set first day to retrieve
date_ref = today
if not incl_today:
    # start at yesterday
   date_ref = date_ref - datetime.timedelta(days = 1)

for i in range(0, backfill_days):
    # API params for target day
    date_from = '%04d-%02d-%02d 00:00:00' % (
            date_ref.year, 
            date_ref.month, 
            date_ref.day
            )
    params['date_from'] = date_from

    # local jsonl file
    dest_file_prefix = '%04d-%02d-%02d' % (
            date_ref.year, 
            date_ref.month, 
            date_ref.day) 

    dest_jsonl_file = '%s/%s.jsonl' % (
            odir,
            dest_file_prefix) 

    # Download only if:
    # * forced
    # * the file does not exist
    # * the incl_today option is set and the ref day is today 
    #   or yesterday
    if (force_download or 
        not os.path.exists(dest_jsonl_file) or
        (incl_today and 
         date_ref in [today, yesterday])):
        log_message(
                1,
                'Getting data for %s' % (
                    date_from
                    )
                )

        # channel 0 (grid consumption and return)
        params['channel'] = 0
        resp = requests.post(
                shelly_cloud_url, 
                data = params)
        grid_resp_dict = resp.json()

        log_message(
                gv_verbose,
                'API Response (%s)\n%s\n' % (
                    params, 
                    json.dumps(grid_resp_dict, indent = 4),
                    )
                )

        # channel 1 (solar production)
        params['channel'] = 1
        resp = requests.post(
                shelly_cloud_url, 
                data = params)
        solar_resp_dict = resp.json()

        log_message(
                gv_verbose,
                'API Response (%s)\n%s\n' % (
                    params, 
                    json.dumps(solar_resp_dict, indent = 4),
                    )
                )

        # populate consumption records
        data_dict = {}
        for shelly_rec in grid_resp_dict['data']['history']:
            usage_rec = {}

            # epoch timestamp from shelly API local time 
            ts, ts_dt = parse_time(
                    shelly_rec['datetime'],
                    grid_resp_dict['data']['timezone'])

            data_dict[ts] = usage_rec

            usage_rec['ts'] = ts
            usage_rec['datetime'] = ts_dt.strftime('%Y/%m/%d %H:%M:%S')
            usage_rec['import'] = shelly_rec['consumption'] / 1000
            usage_rec['export'] = shelly_rec['reversed'] / 1000

            # aggregation keys
            usage_rec['hour'] = ts_dt.hour
            usage_rec['day'] = '%04d-%02d-%02d' % (
                    ts_dt.year, 
                    ts_dt.month, 
                    ts_dt.day)
            usage_rec['month'] = '%04d-%02d' % (
                    ts_dt.year, 
                    ts_dt.month) 
            usage_rec['year'] = '%04d' %(
                    ts_dt.year)
            usage_rec['weekday'] = ts_dt.strftime('%u %a')
            usage_rec['week'] = ts_dt.strftime('%Y-%W')

        # merge in solar production
        for shelly_rec in solar_resp_dict['data']['history']:

            # epoch timestamp from shelly API local time 
            ts, ts_dt = parse_time(
                    shelly_rec['datetime'],
                    grid_resp_dict['data']['timezone'])

            usage_rec = data_dict[ts]
            usage_rec['solar'] = shelly_rec['consumption'] / 1000
            usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
            usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']

        output_results(
                odir,
                output_format,
                data_dict,
                dest_file_prefix,
                decimal_places)

    # move back to previous day
    date_ref = date_ref - datetime.timedelta(days = 1)

