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

    # Report Search API URL and params
    log_message(
            1,
            'Retrieving DA report details for days:%d' % (
                days
                )
            )

    page = 0 # starts at 1 but incremented before GET
    total_pages = 0
    semopx_api_url = 'https://reports.semopx.com/api/v1/documents/static-reports'

    # Params to get DA (Day Ahead) reports only
    # Also retrieving the latest (non-published) report
    params = {}
    params['DPuG_ID'] = 'EA-001'
    params['sort_by'] = 'Date'
    params['order_by'] = 'DESC'
    params['ExcludeDelayedPublication'] = '0'
    params['ResourceName'] = 'MarketResult_SEM-DA_PWR-MRC-D'

    done = False
    report_list = []

    while not done:
        time.sleep(1)

        # incr and set page
        page += 1
        params['page'] = page

        log_message(
                1,
                'Retrieving report page %d/%d (reports:%d)' % (
                    page,
                    total_pages,
                    len(report_list)
                    )
                )

        resp = requests.get(
                semopx_api_url, 
                params = params)
        semopx_resp_dict = resp.json()

        log_message(
                gv_verbose,
                'API Response (%s)\n%s\n' % (
                    params, 
                    json.dumps(semopx_resp_dict, indent = 4),
                    )
                )

        # parse report items
        for item_rec in semopx_resp_dict['items']:
            report = {}
            report['resource_name'] = item_rec['ResourceName']
            report['date'] = item_rec['Date'][:10] # strip to YYYY-MM-DD
            report_list.append(report)

        # pagination
        total_pages = semopx_resp_dict['pagination']['totalPages']
        if page >= total_pages:
            done = True

        # backfill limit
        if len(report_list) >= days:
            done = True
            report_list = report_list[:days]

    log_message(
            gv_verbose,
            'Full Doc List (pages:%d docs:%d)\n%s\n' % (
                page,
                len(report_list),
                json.dumps(report_list, indent = 4),
                )
            )

    # Report Retrieval
    semopx_api_url = 'https://reports.semopx.com/api/v1/documents'

    report_count = 0
    skip_count = 0
    retrieved_count = 0
    total_reports = len(report_list)
    for report in report_list:
        # JSON output file
        json_filename = '%s/%s.jsonl' % (odir, report['date'])

        # check for existing files and skip
        if os.path.exists(json_filename):
            log_message(
                    gv_verbose,
                    'Skipping %s (cached)' % (json_filename)
                    )
            skip_count += 1
            continue

        time.sleep(1)

        report_count += 1
        log_message(
                gv_verbose,
                'Retrieving report %d/%d.. %s' % (
                    report_count,
                    total_reports,
                    report['date'],
                    )
                )

        resp = requests.get(
                semopx_api_url + '/' + report['resource_name'], 
                params = params)
        semopx_resp_dict = resp.json()
        retrieved_count += 1

        log_message(
                gv_verbose,
                'API Response (%s)\n%s\n' % (
                    report['resource_name'], 
                    json.dumps(semopx_resp_dict, indent = 4),
                    )
                )

        # parse document details into data object
        rec_list = []

        # This is a terrible layout of lists
        # within lists in the API
        for data_set_list in semopx_resp_dict['rows']:

            # skip if not desired market area
            # specified as 2nd item in first list
            if data_set_list[0][1] != market_area:
                continue

            # init sub-objects per date/timestamp (string)
            # dates taken from 3rd list
            for date_str in data_set_list[2]:
                data_rec = {}
                ts, local_dt = parse_semopx_time(date_str, timezone)
                data_rec['ts'] = ts
                data_rec['datetime'] = local_dt.strftime('%Y/%m/%d %H:%M:%S')
                data_rec['market_area'] = market_area
                rec_list.append(data_rec)

            # Merge in Euro prices (4th list)
            i = -1
            for euro_price in data_set_list[3]:
                i += 1
                rec_list[i]['euro'] = euro_price

            # Merge in GBP prices (7th list)
            i = -1
            for gbp_price in data_set_list[6]:
                i += 1
                rec_list[i]['gbp'] = gbp_price

        log_message(
                1,
                'Writing.. %s' % (
                    json_filename
                    )
                )
        with open(json_filename, 'w') as f:
            for rec in rec_list:
                f.write(json.dumps(rec) + '\n')

    log_message(
            1,
            'Done.. retrieved %d/%d reports, skipped %d' % (
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
        help = 'Market Area (def ROI-DA) ', 
        default = 'ROI-DA',
        choices = ['ROI-DA', 'NI-DA'],
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

if not os.path.exists(odir):
    os.mkdir(odir)

retrieve_market_results(
        odir = odir,
        days = backfill_days,
        market_area = market_area,
        timezone = timezone)

