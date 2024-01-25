import argparse
import requests
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import hmac
import hashlib
import base64


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


def get_shelly_day_data(
        api_host,
        auth_key,
        device_id,
        date_ref):

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

    # populate consumption records
    data_dict = {}
    for shelly_rec in grid_resp_dict['history']:
        # skip any missing records
        if ('missing' in shelly_rec and 
            shelly_rec['missing']):
            continue

        # epoch timestamp from shelly API local time 
        ts, ts_dt = parse_time(
                shelly_rec['datetime'],
                grid_resp_dict['timezone'])

        # unique key for hour
        # which is also an Excel-friendly datetime
        key = ts_dt.strftime('%Y/%m/%d %H:00:00')

        if key in data_dict:
            usage_rec = data_dict[key]
        else:
            usage_rec = {}
            usage_rec['datetime'] = key
            usage_rec['ts'] = ts
            usage_rec['import'] = 0
            usage_rec['export'] = 0

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
            data_dict[key] = usage_rec

        # add on usage for given time period
        # works with repeat hours in DST rollback
        usage_rec['import'] += shelly_rec['consumption'] / 1000
        usage_rec['export'] += shelly_rec['reversed'] / 1000

    # no data, nothing to do
    if len(data_dict) == 0:
        return None

    return data_dict


# adapted from code
# in https://github.com/Gentleman1983/ginlong_solis_api_connector
def get_solis_cloud_data(
        solis_api_host,
        solis_key_id,
        solis_key_secret,
        url_part, 
        request) -> dict:

    global gv_verbose

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
            solis_key_secret.encode('utf-8'),
            msg = encrypt_str.encode('utf-8'),
            digestmod = hashlib.sha1,
            )
    authorization = 'API %s:%s' % (
            solis_key_id,
            base64.b64encode(hmac_obj.digest()).decode('utf-8')
            )
    headers = {
            'Content-MD5': md5,
            'Content-Type': 'application/json',
            'Date': now,
            'Authorization': authorization,
            }
    log_message(
            gv_verbose,
            'API: \nURL:%s \nHeaders:%s \nrequest:\n%s\n' % (
                solis_api_host + url_part,
                json.dumps(headers, indent = 4),
                json.dumps(request, indent = 4)
                )
            )
    try:
        resp = requests.post(
                solis_api_host + url_part,
                headers = headers,
                json = request)
        log_message(
                gv_verbose,
                'Response:\n%s\n' % (
                    json.dumps(resp.json(), indent = 4)
                    )
                )

        return resp.json()
    except:
        log_message(
                1,
                'Solis API failure.. URL:%s\nStatus:%d \nResp:%s' % (
                    solis_api_host + url_part,
                    resp.status_code,
                    resp.text) 
                )
        return None


def get_solis_day_data(
            solis_api_host,
            solis_key_id,
            solis_key_secret,
            solis_inverter_sn,
            date_ref):

    request = {}
    request['sn'] = solis_inverter_sn
    request['TimeZone'] = 0
    request['time'] = date_ref.strftime('%Y-%m-%d')

    solis_resp = get_solis_cloud_data(
            solis_api_host,
            solis_key_id,
            solis_key_secret,
            '/v1/api/inverterDay', 
            request)

    if not solis_resp:
        return None

    data_dict = {}
    solis_snap_list = solis_resp['data']
    battery_is_present = False

    for solis_snap_rec in solis_snap_list:
        ts = int(solis_snap_rec['dataTimestamp']) // 1000
        ts_dt = datetime.datetime.fromtimestamp(ts)

        # battery detection
        # This is a tad crude but appears to be non-zero
        # for a battery setup and zero otherwise
        if solis_snap_rec['batteryChargingCurrent'] > 0:
            battery_is_present = True

        # unique key for hour
        # which is also an Excel-friendly datetime
        key = ts_dt.strftime('%Y/%m/%d %H:00:00')

        if key in data_dict:
            # retrieve existing
            usage_rec = data_dict[key]
        else:
            # init and index new record
            usage_rec = {}
            usage_rec['datetime'] = key
            usage_rec['ts'] = ts
            usage_rec['solar'] = 0
            usage_rec['import'] = 0
            usage_rec['export'] = 0
            usage_rec['consumed'] = 0
            usage_rec['solar_consumed'] = 0

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

            if battery_is_present:
                usage_rec['battery_charge'] = 0
                usage_rec['battery_discharge'] = 0

            data_dict[key] = usage_rec

        # overwrite acumulated solar generation 
        # to date with max value
        usage_rec['solar'] = max(usage_rec['solar'], solis_snap_rec['eToday'])
        usage_rec['import'] = max(usage_rec['import'], solis_snap_rec['gridPurchasedTodayEnergy'])
        usage_rec['export'] = max(usage_rec['export'], solis_snap_rec['gridSellTodayEnergy'])
        usage_rec['consumed'] = max(usage_rec['consumed'], solis_snap_rec['homeLoadTodayEnergy'])

        if battery_is_present:
            usage_rec['battery_charge'] = max(usage_rec['battery_charge'], solis_snap_rec['batteryTodayChargeEnergy'])
            usage_rec['battery_discharge'] = max(usage_rec['battery_discharge'], solis_snap_rec['batteryTodayDischargeEnergy'])

    # adjust values to relative 
    # difference from previous hours record
    # offset scope is for given day only
    field_list = [
            'solar',
            'import',
            'export',
            'consumed',
            'battery_charge',
            'battery_discharge',
            ]
    offset_dict = {}
    for field in field_list:
        offset_dict[field] = {}

    for key in sorted(data_dict.keys()):
        usage_rec = data_dict[key]

        for field in field_list:

            # not all fields present 
            # such as battery props
            if not field in usage_rec:
                continue

            # offset keyed per unique day
            # init offset to 0 for first
            # encounter of given day
            offset_key = usage_rec['day']
            if not offset_key in offset_dict[field]:
                offset_dict[field][offset_key] = 0

            # adjust accumulated solar to relative
            usage_rec[field] = usage_rec[field] - offset_dict[field][offset_key]

            # negative protection
            if usage_rec[field] < 0:
                usage_rec[field] = 0

            # add relative value to offset for next hour
            offset_dict[field][offset_key] += usage_rec[field]

        # calculate the solar consumed from the adjusted numbers
        usage_rec['solar_consumed'] = usage_rec['solar'] - usage_rec['export'] 
        if usage_rec['solar_consumed'] < 0:
            usage_rec['solar_consumed'] = 0

    return data_dict


def get_day_data(
        odir,
        date_ref,
        solis_api_host,
        solis_key_id,
        solis_key_secret,
        solis_inverter_sn,
        shelly_api_host,
        shelly_auth_key,
        shelly_device_id):

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
        # file already exists.. only overwrite if partial
        # property present in first record

        # get first record
        fp = open(dest_jsonl_file)
        line = fp.readline()
        rec = json.loads(line)

        # rec will have partial property if it 
        # was a partial read
        if not 'partial' in rec:
            log_message(
                    gv_verbose,
                    'Skipping %s (already complete)' % (
                        dest_jsonl_file
                        )
                    )
            return

        # Present as an update of 
        # a peviously incomplete file
        write_context = 'Updating'

    partial_data = False

    solis_dict = get_solis_day_data(
            solis_api_host,
            solis_key_id,
            solis_key_secret,
            solis_inverter_sn,
            date_ref)

    # delay between calls
    # solis will reject them otherwise
    time.sleep(3)

    if not solis_dict:
        # this only applies to API failure
        # so best to walk away and try again later
        return

    # partial check
    # number of recs can be < 24 here for a string
    # inverter. 
    # so we gauge the partial for records with latest activity less than 2 
    # hours ago. 
    latest_rec = solis_dict[sorted(solis_dict.keys())[-1]]
    now = int(time.time())
    if now - latest_rec['ts'] < 7200:
        partial_data = True

    # optional Shelly data
    if (shelly_api_host and 
        shelly_device_id and 
        shelly_auth_key):
        shelly_dict = get_shelly_day_data(
                api_host = shelly_api_host,
                auth_key = shelly_auth_key,
                device_id = shelly_device_id,
                date_ref = date_ref)

        # Shelly either has 24 records 
        # or not for partal determination. 
        if (not shelly_dict or 
            len(shelly_dict) < 24):
            partial_data = True

        # merge
        if shelly_dict:
            for key in shelly_dict:
                shelly_rec = shelly_dict[key]
                if key in solis_dict:
                    # merge import and export
                    solis_rec = solis_dict[key]

                    solis_rec['import'] = shelly_rec['import']
                    solis_rec['export'] = shelly_rec['export']
                    solis_rec['ts'] = shelly_rec['ts']
                    solis_rec['solar_consumed'] = solis_rec['solar'] - solis_rec['export']
                    solis_rec['consumed'] = solis_rec['import'] + solis_rec['solar_consumed']
                else:
                    solis_rec = shelly_rec
                    solis_rec['solar'] = 0
                    solis_rec['solar_consumed'] = 0
                    solis_rec['consumed'] = solis_rec['import']
                    solis_dict[key] = solis_rec

    if partial_data:
        for key in solis_dict:
            solis_dict[key]['partial'] = True

    # write JSONL File
    log_message(
            1,
            '%s %s' % (
                write_context,
                dest_jsonl_file
                )
            )
    with open(dest_jsonl_file, 'w') as f:
        for key in sorted(solis_dict.keys()):
            f.write(json.dumps(solis_dict[key]) + '\n')

    return


# main()

# default storage dir for data
home = os.path.expanduser('~')
default_odir = home + '/.solisdata'   

parser = argparse.ArgumentParser(
        description = 'Solis Inverter Data Retrieval Utility'
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
        '--solis_inverter_sn', 
        help = 'Solis Inverter Serial Number', 
        required = True
        )

parser.add_argument(
        '--solis_api_host', 
        help = 'Solis Inverter API Host', 
        required = True
        )

parser.add_argument(
        '--solis_key_id', 
        help = 'Solis Inverter API Key ID', 
        required = True
        )

parser.add_argument(
        '--solis_key_secret', 
        help = 'Solis Inverter API Key Secret', 
        required = True
        )

parser.add_argument(
        '--shelly_api_host', 
        help = 'Shelly API Host', 
        required = False
        )

parser.add_argument(
        '--shelly_device_id', 
        help = 'Shelly Device ID', 
        required = False
        )

parser.add_argument(
        '--shelly_auth_key', 
        help = 'Shelly API Auth Key', 
        required = False
        )

parser.add_argument(
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
backfill_days = args['days']
odir = args['odir']
solis_inverter_sn = args['solis_inverter_sn']
solis_api_host = args['solis_api_host']
solis_key_id = args['solis_key_id']
solis_key_secret = args['solis_key_secret']
shelly_api_host = args['shelly_api_host']
shelly_device_id = args['shelly_device_id']
shelly_auth_key = args['shelly_auth_key']
gv_verbose = args['verbose']

# JSON encoder force decimal places to 5
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.5f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

if not os.path.exists(odir):
    os.mkdir(odir)

# Set first day as today
date_ref = datetime.date.today()

for i in range(0, backfill_days):

    get_day_data(
            odir,
            date_ref,
            solis_api_host,
            solis_key_id,
            solis_key_secret,
            solis_inverter_sn,
            shelly_api_host,
            shelly_auth_key,
            shelly_device_id)

    # move back to previous day
    date_ref = date_ref - datetime.timedelta(days = 1)
