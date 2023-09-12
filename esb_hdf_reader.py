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


def get_hours_in_day(
        datetime_str,
        timezone):

    # naive parse of our datetime field
    dt = datetime.datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')

    # assert local timezone
    dt = dt.replace(tzinfo = zoneinfo.ZoneInfo(timezone))

    # reset to current day midnight
    # and get dt for the next day 
    dt_midnight = dt.replace(
            hour = 0,
            minute = 0,
            second = 0,
            )
    dt_next_midnight = dt_midnight + datetime.timedelta(days = 1)

    # to epoch second timestamps and subtract
    # and get number of local hours in day
    daylen_secs = int(dt_next_midnight.timestamp()) - int(dt_midnight.timestamp())
    daylen_hours = daylen_secs / 3600

    return daylen_hours


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
        '--timezone', 
        help = 'Timezone', 
        default = 'Europe/Dublin',
        required = False
        )

parser.add_argument(
        '--decimal_places', 
        help = 'Decimal Places (def:4)', 
        type = int,
        default = 4,
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
output_format = args['format']
timezone = args['timezone']
decimal_places = args['decimal_places']
verbose = args['verbose']

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
        usage_rec['datetime'] = dt_ref.strftime('%Y/%m/%d %H:%M:%S')
        usage_rec['import'] = 0
        usage_rec['consumed'] = 0
        usage_rec['export'] = 0

        # aggregation keys
        usage_rec['hour'] = dt_ref.hour
        usage_rec['day'] = '%04d-%02d-%02d' % (
                dt_ref.year, 
                dt_ref.month, 
                dt_ref.day)
        usage_rec['month'] = '%04d-%02d' % (
                dt_ref.year, 
                dt_ref.month) 
        usage_rec['year'] = '%04d' %(
                dt_ref.year)
        usage_rec['weekday'] = dt_ref.strftime('%u %a')
        usage_rec['week'] = dt_ref.strftime('%Y-%W')
    else:
        # retrieve usage rec
        usage_rec = usage_dict[ts_ref]

    # Import usage
    if esb_rec['type'] == 'Active Import Interval (kW)':
        # append 30-min usage value / 2 
        usage_rec['import'] += float(esb_rec['value']) / 2
        # align consumed to current value
        usage_rec['consumed'] = usage_rec['import']

    # Export
    if esb_rec['type'] == 'Active Export Interval (kW)':
        # append 30-min usage value / 2 
        usage_rec['export'] += float(esb_rec['value']) / 2

log_message(
        1,
        'Parsed %d hourly records from %s' % (
            len(usage_dict),
            hdf_file,
            )
        )

# split into separate dicts per day
day_dict = {}
for ts in usage_dict:
    usage_rec = usage_dict[ts]
    day = usage_rec['day']
    if not day in day_dict:
        day_dict[day] = {}

    day_dict[day][ts] = usage_rec

# Check for full 24h coverage per day
# purging incomplete days
for day in list(day_dict.keys()):
    # get datetime of first item in dict
    # actual one we pick does not matter
    # we need to then determine how long that day
    # is in hours
    first_ts = next(iter(day_dict[day]))
    first_datetime = day_dict[day][first_ts]['datetime']
    expected_day_hours = get_hours_in_day(
            first_datetime,
            timezone)

    # then check how many hours we actually have tracked
    tracked_hours = len(day_dict[day])

    # purge if the tracked does not match the expected
    if tracked_hours != expected_day_hours:
        log_message(
                1,
                'Purging incompete day %s.. %d/%d hours present' % (
                    day,
                    tracked_hours,
                    expected_day_hours
                    )
                )
        del day_dict[day]


# JSON encoder force decimal places to 3
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

for day in day_dict:
    output_results(
            odir,
            output_format,
            day_dict[day],
            day,
            decimal_places)
