import argparse
import requests
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import sys


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


def parse_semopx_time(
        datetime_str,
        timezone):

    # Parse SEMOpx UTC time to DT
    # this has a "Z" inicator the parse will corectly
    # assert a UTC timezone
    utc_dt = dateutil.parser.parse(datetime_str)

    # convert go epoch as God intended
    time_stamp = int(utc_dt.timestamp())

    # Localise to specified local timezone
    local_dt = utc_dt.astimezone(zoneinfo.ZoneInfo(timezone))

    # return both values
    return time_stamp, local_dt


def retrieve_market_results(
        odir, 
        days,
        market_area,
        timezone):

    global gv_verbose

    semopx_api_query_url = 'https://reports.semopx.com/api/v1/documents/static-reports'
    semopx_api_retrieval_url = 'https://reports.semopx.com/api/v1/documents'

    # Report Search API URL and params
    log_message(
            1,
            'Retrieving SEMOpx report details for days:%d' % (
                days
                )
            )

    page = 0 # starts at 1 but incremented before GET
    total_pages = 0

    # Params to get market data (Day Ahead + IDA1-3) reports only
    # Also retrieving the latest (non-published) report
    params = {}
    params['DPuG_ID'] = 'EA-001'
    params['sort_by'] = 'Date'
    params['order_by'] = 'DESC'
    params['ExcludeDelayedPublication'] = '0'

    done = False
    report_dict = {}

    while not done:
        # 1-sec call interval to avoid 
        # stress on the API
        time.sleep(1)

        # incr and set page
        page += 1
        params['page'] = page

        resp = requests.get(
                semopx_api_query_url, 
                params = params)
        semopx_resp_dict = resp.json()

        log_message(
                gv_verbose,
                'API Response %s (%s)\n%s\n' % (
                    semopx_api_query_url,
                    params, 
                    json.dumps(semopx_resp_dict, indent = 4),
                    )
                )

        # parse report items
        for item_rec in semopx_resp_dict['items']:
            # key by YYYY-MM-DD
            key_date = item_rec['Date'][:10] # strip to YYYY-MM-DD
            if not key_date in report_dict:
                report = {}
                report['date'] = key_date
                report['resources'] = []
                report_dict[key_date] = report
            else:
                report = report_dict[key_date]

            # append report resource name to list
            report['resources'].append(item_rec['ResourceName'])

        # pagination
        total_pages = semopx_resp_dict['pagination']['totalPages']
        if page >= total_pages:
            done = True

        # backfill limit
        # we allow it to exceed the limit (> desired days)
        # instead of >=. That helps to get a complete day as much as 
        # possible.
        # Then we get the sorted key list, skip the leading number of keys
        # and purge the rest
        if len(report_dict) > days:
            done = True
            key_list = list(report_dict.keys())
            key_list.sort(reverse = True)
            key_list = key_list[days:]
            for purge_key in key_list:
                del report_dict[purge_key]

        log_message(
                1,
                'Retrieved page %d/%d (days:%d)' % (
                    page,
                    total_pages,
                    len(report_dict)
                    )
                )

    log_message(
            gv_verbose,
            'Full report list (pages:%d days:%d)\n%s' % (
                page,
                len(report_dict),
                json.dumps(report_dict, indent = 4),
                )
            )

    # Report Data Retrieval
    report_count = 0
    skip_count = 0
    retrieved_count = 0
    total_reports = len(report_dict)
    for key in report_dict:
        report_count += 1
        report = report_dict[key]

        # JSON output file
        json_filename = '%s/%s.jsonl' % (odir, report['date'])

        # check for complete data sets
        if os.path.exists(json_filename):
            # load file into dict
            with open(json_filename, 'r') as f:
                # parse into dict
                rec_dict = {}
                for line in f:
                    rec = json.loads(line)
                    ts = rec['ts']
                    rec_dict[ts] = rec

                da_present = False
                ida1_present = False
                ida2_present = False
                ida3_present = False

                for ts in rec_dict:
                    rec = rec_dict[ts]
                    if 'da_kwh_rate' in rec:
                        da_present = True
                    if 'ida1_kwh_rate' in rec:
                        ida1_present = True
                    if 'ida2_kwh_rate' in rec:
                        ida2_present = True
                    if 'ida3_kwh_rate' in rec:
                        ida3_present = True

                log_message(gv_verbose,
                            'Checks: filename:%s DA:%s IDA1:%s IDA2:%s IDA3:%s' % (
                                json_filename,
                                da_present,
                                ida1_present,
                                ida2_present,
                                ida3_present
                                )
                            )

                # complete record has data from all auctions
                if (da_present and 
                    ida1_present and
                    ida2_present and
                    ida3_present):
                    log_message(
                            gv_verbose,
                            'Skipping %s (cached)' % (json_filename)
                            )
                    skip_count += 1
                    continue

        # 1-sec delay between API calls
        time.sleep(1)

        retrieved_count += 1
        log_message(
                gv_verbose,
                'Retrieving %d resources for report %d/%d.. %s' % (
                    len(report['resources']),
                    report_count,
                    total_reports,
                    report['date'],
                    )
                )

        # parse document details into dict of objects, one per timestamp
        rec_dict = {}

        for resource_name in report['resources']:
            # get specific report appending resource name to base URL
            url = semopx_api_retrieval_url + '/' + resource_name
            resp = requests.get(
                    url,
                    params = params)
            semopx_resp_dict = resp.json()

            log_message(
                    gv_verbose,
                    'API Response %s\n%s\n' % (
                        url,
                        json.dumps(semopx_resp_dict, indent = 4),
                        )
                    )

            # data context
            if 'SEM-DA' in resource_name:
                context_prefix = 'da_'
            elif 'SEM-IDA1' in resource_name:
                context_prefix = 'ida1_'
            elif 'SEM-IDA2' in resource_name:
                context_prefix = 'ida2_'
            elif 'SEM-IDA3' in resource_name:
                context_prefix = 'ida3_'
            else:
                # ignore this unrecognised resource
                log_message(
                        gv_verbose,
                        'Ignoring unsupported resource %s' % (
                            resource_name,
                            )
                        )
                continue

            # This is an awkward response layout of lists
            # within lists 
            for data_set_list in semopx_resp_dict['rows']:

                # skip if not desired market area
                # specified in 2nd item in first list
                # The values are <AREA>-DA, <AREA>-IDA1, 
                # <AREA>-IDA2, <AREA>-IDA3
                # so we test for sub-string
                if not market_area in data_set_list[0][1]:
                    continue

                # init sub-objects per date/timestamp (string)
                # dates taken from 3rd list
                # These vary from per-hour or per-30-min boundaries
                key_list = []
                for date_str in data_set_list[2]:
                    ts, local_dt = parse_semopx_time(date_str, timezone)

                    # track list of keys in this encountered order
                    # as other related lists are index-synced to these timestamps
                    key_list.append(ts)

                    # init record in main dict if not present
                    if not ts in rec_dict:
                        data_rec = {}
                        data_rec['ts'] = ts
                        data_rec['datetime'] = local_dt.strftime('%Y/%m/%d %H:%M:%S')
                        data_rec['market_area'] = market_area
                        rec_dict[ts] = data_rec

                # Merge in Euro prices (4th list)
                if market_area == 'ROI':
                    i = -1
                    for euro_price in data_set_list[3]:
                        i += 1
                        ts = key_list[i]
                        rec_dict[ts]['currency'] = 'euro'
                        rec_dict[ts][context_prefix + 'kwh_rate'] = euro_price / 1000

                # Merge in GBP prices (7th list)
                if market_area == 'NI':
                    i = -1
                    for gbp_price in data_set_list[6]:
                        i += 1
                        ts = key_list[i]
                        rec_dict[ts]['currency'] = 'gbp'
                        rec_dict[ts][context_prefix + 'kwh_rate'] = gbp_price / 1000


        # day-ahead merge into :30-min records
        # check each record if it ends with :00:00 (on the hour)
        # find the next :30 record and copy the DA prices
        for ts in sorted(rec_dict.keys()):
            rec = rec_dict[ts]
            if rec['datetime'].endswith(':00:00'):
                # next :30 timestamp and datetime
                next_ts = ts + 1800
                utc_dt = datetime.datetime.fromtimestamp(next_ts, datetime.UTC)
                next_dt = utc_dt.astimezone(zoneinfo.ZoneInfo(timezone))

                if next_ts in rec_dict:
                    next_rec = rec_dict[next_ts]
                else:
                    next_rec = {}
                    next_rec['ts'] = next_ts
                    next_rec['datetime'] = next_dt.strftime('%Y/%m/%d %H:%M:%S')
                    next_rec['market_area'] = market_area
                    rec_dict[next_ts] = next_rec

                # copy forward the DA price if present
                if 'da_kwh_rate' in rec:
                    next_rec['da_kwh_rate'] = rec['da_kwh_rate']


        # set final rate based on pecking order
        # from IDA3 to DA
        for ts in rec_dict.keys():
            rec = rec_dict[ts]
            if 'ida3_kwh_rate' in rec_dict[ts]:
                rec['final_kwh_rate'] = rec['ida3_kwh_rate']
            elif 'ida2_kwh_rate' in rec_dict[ts]:
                rec['final_kwh_rate'] = rec['ida2_kwh_rate']
            elif 'ida1_kwh_rate' in rec_dict[ts]:
                rec['final_kwh_rate'] = rec['ida1_kwh_rate']
            elif 'da_kwh_rate' in rec_dict[ts]:
                rec['final_kwh_rate'] = rec['da_kwh_rate']


        log_message(
                1,
                'Writing.. file %d/%d %s' % (
                    report_count,
                    total_reports,
                    json_filename
                    )
                )
        with open(json_filename, 'w') as f:
            for ts in sorted(rec_dict.keys()):
                rec = rec_dict[ts]
                f.write(json.dumps(rec) + '\n')

    log_message(
            1,
            'Done.. retrieved %d/%d reports, skipped %d (cached)' % (
                retrieved_count,
                total_reports,
                skip_count
                )
            )        
    return


# main()

# default storage dir for data
home = os.path.expanduser('~')
default_odir = home + '/.semopxdata'   

parser = argparse.ArgumentParser(
        description = 'SEMOpx Data Retrieval Utility'
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory for generated files', 
        default = default_odir,
        required = False
        )

parser.add_argument(
        '--days', 
        help = 'Backfill days (def 5)', 
        type = int,
        default = 5,
        required = False
        )

parser.add_argument(
        '--market', 
        help = 'Market Area (def ROI) ', 
        default = 'ROI',
        choices = ['ROI', 'NI'],
        required = False
        )

parser.add_argument(
        '--timezone', 
        help = 'Timezone def:Europe/Dublin', 
        default = 'Europe/Dublin',
        required = False
        )

parser.add_argument(
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
odir = args['odir']
backfill_days = args['days']
market_area = args['market']
timezone = args['timezone']
gv_verbose = args['verbose']

# JSON encoder force decimal places to 4
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

if not os.path.exists(odir):
    os.mkdir(odir)

retrieve_market_results(
        odir = odir,
        days = backfill_days,
        market_area = market_area,
        timezone = timezone)

