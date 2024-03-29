import argparse
import requests
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo


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


def get_day_data(
        api_host,
        auth_key,
        device_id,
        date_ref,
        odir,
        solar_discard):

    global gv_verbose

    # API URL and params
    shelly_cloud_url = 'https://%s/v2/statistics/power-consumption/em-1p' % (api_host)
    params = {}
    params['id'] = device_id
    params['auth_key'] = auth_key
    params['date_range'] = 'day'

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

    # default behaviour is to report 
    # as a standard write
    write_context = 'Writing'

    # Check if the target file exists
    if os.path.exists(dest_jsonl_file):
        # file already exists.. only download if partial
        # property present in first record

        # get first record
        fp = open(dest_jsonl_file)
        line = fp.readline()
        rec = json.loads(line)

        # rec will have partial property if it 
        # was a partial read
        if not 'partial' in rec:
            return

        # Present as an update of 
        # a peviously incomplete file
        write_context = 'Updating'

    # channel 0 (grid consumption and return)
    params['channel'] = 0
    resp = requests.get(
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
    resp = requests.get(
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
            usage_rec['solar_discard'] = 0
            usage_rec['ts'] = ts
            usage_rec['datetime'] = ts_dt.strftime('%Y/%m/%d %H:%M:%S')

            # ts and aggregation keys
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

        # solar
        solar = shelly_rec['consumption'] / 1000

        # zero any value <= the solar discard
        # caters for neglible error readings at night
        # Also subtract if value exceeds twice the discard
        if solar <= solar_discard:
            usage_rec['solar_discard'] += solar
            solar = 0
        elif solar >= solar_discard:
            solar -= solar_discard
            usage_rec['solar_discard'] += solar_discard

        # append the solar value 
        usage_rec['solar'] += solar

        # generate/re-generate the consumed fields
        # solar_consumed is zeroed if it goes negative due to the discard
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export']
        if usage_rec['solar_consumed'] < 0:
            usage_rec['solar_consumed'] = 0
        usage_rec['consumed'] = usage_rec['import'] + usage_rec['solar_consumed']

    # no data, nothing to do
    if len(data_dict) == 0:
        return

    # mark all records partial
    # if we had encountered missing data
    if partial_data:
        for key in data_dict.keys():
            data_dict[key]['partial'] = True

    # write JSONL File
    log_message(
            1,
            '%s %s' % (
                write_context,
                dest_jsonl_file
                )
            )
    with open(dest_jsonl_file, 'w') as f:
        for key in sorted(data_dict.keys()):
            f.write(json.dumps(data_dict[key]) + '\n')

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
        '--days', 
        help = 'Backfill in days (def 30)', 
        type = int,
        default = 30,
        required = False
        )

parser.add_argument(
        '--solar_discard', 
        help = 'per-hour error discard for Solar (kWh)', 
        type = float,
        default = 0,
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
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
api_host = args['host']
backfill_days = args['days']
odir = args['odir']
device_id = args['id']
solar_discard = args['solar_discard']
auth_key = args['auth_key']
gv_verbose = args['verbose']

# JSON encoder force decimal places to 5
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.5f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

if not os.path.exists(odir):
    os.mkdir(odir)

# Set first day to retrieve as today
# note this is a date and not a datetime
date_ref = datetime.date.today() 

for i in range(0, backfill_days):
    get_day_data(
            api_host = api_host,
            auth_key = auth_key,
            device_id = device_id,
            date_ref = date_ref,
            odir = odir,
            solar_discard = solar_discard)

    # move back to previous day
    date_ref = date_ref - datetime.timedelta(days = 1)

