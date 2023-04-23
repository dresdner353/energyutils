import argparse
import json
import os
import time
import datetime
import zoneinfo
import csv
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


def parse_esb_time(
        datetime_str,
        timezone):

    # naive parse
    if '/' in datetime_str:
        dt = datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
    else:
        dt = datetime.datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')

    # assert local timezone
    dt = dt.replace(tzinfo = zoneinfo.ZoneInfo(timezone))

    # convert go epoch as God intended
    time_stamp = int(dt.timestamp())

    # return both values
    return time_stamp, dt


def parse_range_time(
        datetime_str,
        timezone,
        end):

    # naive parse
    dt = datetime.datetime.strptime(datetime_str, '%Y%m%d')

    # end of day
    if end:
        dt = dt.replace(
                hour = 23,
                minute = 59,
                second = 59
                )

    # assert local timezone
    dt = dt.replace(tzinfo = zoneinfo.ZoneInfo(timezone))

    # convert go epoch as God intended
    time_stamp = int(dt.timestamp())

    # return both values
    return time_stamp, dt


def output_results(
        odir,
        data_dict,
        prefix,
        title,
        decimal_places):

    # no date, nothing to do
    if len(data_dict) == 0:
        return

    # JSONL File
    dest_jsonl_file = '%s/%s_%s.jsonl' % (odir, prefix, title)
    log_message(
            1,
            'Writing %s data to %s' % (
                title,
                dest_jsonl_file)
            )
    with open(dest_jsonl_file, "w") as f:
        for key in sorted(data_dict.keys()):
            f.write(json.dumps(data_dict[key]) + '\n')

    # CSV File
    first_key = list(data_dict.keys())[0]
    first_rec = data_dict[first_key]
    field_list = list(first_rec.keys())
    field_list.sort()
    dest_csv_file = '%s/%s_%s.csv' % (odir, prefix, title)
    log_message(
            1,
            'Writing %s data to %s' % (
                title,
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
parser = argparse.ArgumentParser(
        description = 'ESB HDF Reader'
        )

parser.add_argument(
        '--file', 
        help = 'ESB HDF file', 
        required = True
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory', 
        required = True
        )

parser.add_argument(
        '--start', 
        help = 'Calculation Start Date (YYYYMMDD)', 
        required = False
        )

parser.add_argument(
        '--end', 
        help = 'Calculation End Date (YYYYMMDD)', 
        required = False
        )

parser.add_argument(
        '--timezone', 
        help = 'Timezone', 
        default = 'Europe/Dublin',
        required = False
        )

parser.add_argument(
        '--tariff_rate', 
        help = 'kwh Tariff <NAME:rate/kWh> <NAME:rate/kWh> ...', 
        nargs = '+',
        required = False
        )

parser.add_argument(
        '--tariff_interval', 
        help = 'Time Interval for Tariff <HH:HH:Tariff Name> <HH:HH:Tariff Name> ...', 
        nargs = '+',
        required = False
        )

parser.add_argument(
        '--fit_rate', 
        help = 'FIT Rate rate/kWh', 
        type = float,
        required = False
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
hdf_file = args['file']
odir = args['odir']
start_date = args['start']
end_date = args['end']
timezone = args['timezone']
tariff_list = args['tariff_rate']
interval_list = args['tariff_interval']
fit_rate = args['fit_rate']
decimal_places = args['decimal_places']
verbose = args['verbose']
verbose = args['verbose']

# tariffs 
tariff_dict = {}
if tariff_list:
    for tariff_str in tariff_list:
        fields = tariff_str.split(':')
        if len(fields) == 2:
            tariff_dict[fields[0]] = float(fields[1])

    log_message(
            verbose,
            'Tariff Rates: %s' % (
                tariff_dict)
            )

# tariff intervals
tarff_interval_dict = {}
if interval_list:
    for interval_str in interval_list:
        fields = interval_str.split(':')
        if len(fields) == 3:
            start_hh = int(fields[0])
            end_hh = int(fields[1])
            tariff_name = fields[2]

            while start_hh != end_hh:
                if tariff_name in tariff_dict:
                    tarff_interval_dict[start_hh] = tariff_name
                    start_hh = (start_hh + 1) % 24
    log_message(
            verbose,
            'Tariff Intervals: %s' % (
                tarff_interval_dict)
            )

    if len(tarff_interval_dict) != 24:
        log_message(
                1,
                'WARNING: Tariff interval data present for only %d/24 hours' % (
                    len(tarff_interval_dict))
                )


# start/end range
start_ts = 0
end_ts = 0
start_dt = None
end_dt = None
if start_date:
    start_ts, start_dt = parse_range_time(
            start_date,
            timezone,
            end = False)

if end_date:
    end_ts, end_dt = parse_range_time(
            end_date,
            timezone,
            end = True)

# ESB HDF Parse
fields = [
        'mprn', 
        'serial', 
        'value', 
        'type', 
        'datetime'
        ]

reader = csv.DictReader(
        open(hdf_file),
        delimiter = ',',
        quotechar = '"',
        fieldnames = fields
        )

usage_dict = {}

row_num = -1
for esb_rec in reader:
    row_num += 1

    # skip header row
    if row_num == 0:
        continue

    # parse the ESB local time
    ts, dt = parse_esb_time(
            esb_rec['datetime'],
            timezone
            )
    
    # Adjust time to common of hour from within usage occurred
    # ESB report time at end of measurement
    # So we roll :30 -> :00 and :00 back to previous hour
    if dt.minute == 30:
        # roll back to start of hour
        dt_ref = dt.replace(
            minute = 0,
            )
    else:
        # roll back 1 hour
        dt_ref = dt - datetime.timedelta(hours = 1)

    # Get epoch of the reference hour
    ts_ref = int(dt_ref.timestamp())

    # get usage rec (create or retrieve)
    if not ts_ref in usage_dict:
        # init usage rec
        usage_rec = {}
        usage_dict[ts_ref] = usage_rec
        usage_rec['ts'] = ts_ref
        usage_rec['datetime'] = dt_ref.strftime("%Y/%m/%d %H:%M:%S")
        usage_rec['import'] = 0
        usage_rec['export'] = 0
        usage_rec['tariff_name'] = 'N/A'
        usage_rec['tariff_rate'] = 0
        usage_rec['import_cost'] = 0
        usage_rec['export_credit'] = 0

        # aggregation keys
        usage_rec['hour'] = dt_ref.hour
        usage_rec['day'] = '%04d%02d%02d' % (
                dt_ref.year, 
                dt_ref.month, 
                dt_ref.day)
        usage_rec['month'] = '%04d%02d' % (
                dt_ref.year, 
                dt_ref.month) 
        usage_rec['year'] = '%04d' %(
                dt_ref.year)
    else:
        # retrieve usage rec
        usage_rec = usage_dict[ts_ref]

    # Import usage
    if esb_rec['type'] == 'Active Import Interval (kW)':
        # append 30-min usage value / 2 
        usage_rec['import'] += float(esb_rec['value']) / 2

        if dt_ref.hour in tarff_interval_dict:
            # set tariff detail and calculate cost
            usage_rec['tariff_name'] = tarff_interval_dict[dt_ref.hour]
            usage_rec['tariff_rate'] = tariff_dict[usage_rec['tariff_name']]
            usage_rec['import_cost'] = usage_rec['import'] * usage_rec['tariff_rate'] 

    if esb_rec['type'] == 'Active Export Interval (kW)':
        # append 30-min usage value / 2 
        usage_rec['export'] += float(esb_rec['value']) / 2

        if fit_rate:
            usage_rec['export_credit'] = usage_rec['export'] * fit_rate

log_message(
        1,
        'Parsed %d hourly records from %s' % (
            len(usage_dict),
            hdf_file,
            )
        )

# aggregations
year_dict = {}
month_dict = {}
day_dict = {}
hour_dict = {}
tariff_dict = {}

for ts in sorted(usage_dict.keys()):
    usage_rec = usage_dict[ts]

    # skip records if out of range
    if (start_ts and 
        usage_rec['ts'] < start_ts):
        continue

    if (end_ts and 
        usage_rec['ts'] > end_ts):
        continue

    year =  usage_rec['year']
    month =  usage_rec['month']
    day =  usage_rec['day']
    hour =  usage_rec['hour']
    tariff_name = usage_rec['tariff_name']
    tariff_rate = usage_rec['tariff_rate']

    if not year in year_dict:
        year_dict[year] = {}
        year_dict[year]['year'] = year
        year_dict[year]['import'] = 0
        year_dict[year]['import_cost'] = 0
        year_dict[year]['export'] = 0
        year_dict[year]['export_credit'] = 0
    year_dict[year]['import'] += usage_rec['import']
    year_dict[year]['import_cost'] += usage_rec['import_cost']
    year_dict[year]['export'] += usage_rec['export']
    year_dict[year]['export_credit'] += usage_rec['export_credit']

    if not month in month_dict:
        month_dict[month] = {}
        month_dict[month]['month'] = month
        month_dict[month]['import'] = 0
        month_dict[month]['import_cost'] = 0
        month_dict[month]['export'] = 0
        month_dict[month]['export_credit'] = 0
    month_dict[month]['import'] += usage_rec['import']
    month_dict[month]['import_cost'] += usage_rec['import_cost']
    month_dict[month]['export'] += usage_rec['export']
    month_dict[month]['export_credit'] += usage_rec['export_credit']

    if not day in day_dict:
        day_dict[day] = {}
        day_dict[day]['day'] = day
        day_dict[day]['import'] = 0
        day_dict[day]['import_cost'] = 0
        day_dict[day]['export'] = 0
        day_dict[day]['export_credit'] = 0
    day_dict[day]['import'] += usage_rec['import']
    day_dict[day]['import_cost'] += usage_rec['import_cost']
    day_dict[day]['export'] += usage_rec['export']
    day_dict[day]['export_credit'] += usage_rec['export_credit']

    if not hour in hour_dict:
        hour_dict[hour] = {}
        hour_dict[hour]['hour'] = hour
        hour_dict[hour]['import'] = 0
        hour_dict[hour]['import_cost'] = 0
        hour_dict[hour]['export'] = 0
        hour_dict[hour]['export_credit'] = 0
    hour_dict[hour]['import'] += usage_rec['import']
    hour_dict[hour]['import_cost'] += usage_rec['import_cost']
    hour_dict[hour]['export'] += usage_rec['export']
    hour_dict[hour]['export_credit'] += usage_rec['export_credit']

    if not tariff_name in tariff_dict:
        tariff_dict[tariff_name] = {}
        tariff_dict[tariff_name]['tariff'] = tariff_name
        tariff_dict[tariff_name]['rate'] = tariff_rate
        tariff_dict[tariff_name]['import'] = 0
        tariff_dict[tariff_name]['import_cost'] = 0
        tariff_dict[tariff_name]['export'] = 0 
        tariff_dict[tariff_name]['export_credit'] = 0
    tariff_dict[tariff_name]['import'] += usage_rec['import']
    tariff_dict[tariff_name]['import_cost'] += usage_rec['import_cost']

    if fit_rate:
        if not 'FIT' in tariff_dict:
            tariff_dict['FIT'] = {}
            tariff_dict['FIT']['tariff'] = 'FIT'
            tariff_dict['FIT']['rate'] = fit_rate
            tariff_dict['FIT']['import'] = 0
            tariff_dict['FIT']['import_cost'] = 0
            tariff_dict['FIT']['export'] = 0
            tariff_dict['FIT']['export_credit'] = 0

        tariff_dict['FIT']['export'] += usage_rec['export']
        tariff_dict['FIT']['export_credit'] += usage_rec['export_credit']


log_message(
        1,
        'Cost Calculation between %s <--> %s' % (
            start_dt.isoformat() if start_dt else 'N/A',
            end_dt.isoformat() if end_dt else 'N/A')
        )

class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

# JSON encoder force decimal places to 3
json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

basename = os.path.basename(hdf_file)
prefix = os.path.splitext(basename)[0]

if len(tariff_dict) > 0:
    output_results(
            odir,
            tariff_dict,
            prefix,
            'tariff',
            decimal_places)

output_results(
        odir,
        usage_dict,
        prefix,
        'all',
        decimal_places)

output_results(
        odir,
        year_dict,
        prefix,
        'year',
        decimal_places)

output_results(
        odir,
        month_dict,
        prefix,
        'month',
        decimal_places)

output_results(
        odir,
        day_dict,
        prefix,
        'day',
        decimal_places)

output_results(
        odir,
        hour_dict,
        prefix,
        'hour',
        decimal_places)
