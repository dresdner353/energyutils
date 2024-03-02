import argparse
import json
import os
import time
import datetime
import zoneinfo
import sys
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
    # and get actual number of local hours in day
    daylen_secs = int(dt_next_midnight.timestamp()) - int(dt_midnight.timestamp())
    daylen_hours = daylen_secs / 3600

    # set to min of 24 and calculated hours
    # A winter DST adjustment day will have 25
    # hours because of the rollback. 
    # But ESB data reports that extra hour as one time
    # so we will only see 24 hours reported
    daylen_hours = min(24, daylen_hours)

    return daylen_hours


def process_esb_hdf_files(
        hdf_file_list,
        timezone,
        odir,
        partial_days):

    # ESB HDF Parse
    fields = [
            'mprn', 
            'serial', 
            'value', 
            'type', 
            'datetime'
            ]

    # parse all ESB HDF files into a dict of the 30-min records
    # some records will overwrite each other
    esb_dict = {}
    for hdf_file in hdf_file_list:
        reader = csv.DictReader(
                open(hdf_file),
                delimiter = ',',
                quotechar = '"',
                fieldnames = fields
                )
        
        row_num = -1
        for hdf_rec in reader:
            row_num += 1
        
            # skip header row
            if row_num == 0:
                continue
        
            # parse the ESB local time
            ts, dt = parse_esb_time(
                    hdf_rec['datetime'],
                    timezone
                    )
            
            # Adjust time to common hour from within usage occurred
            # ESB report time at end of measurement
            # So we roll :30 -> :00 and :00 back to previous hour
            if dt.minute == 30:
                # :30 -> roll back to start of hour
                dt_ref = dt.replace(
                    minute = 0,
                    )
            else:
                # :00 -> roll back 1 hour
                dt_ref = dt - datetime.timedelta(hours = 1)
        
            # Get epoch of the common reference hour
            ts_ref = int(dt_ref.timestamp())
        
            # get usage rec (create or retrieve)
            # this uses the original ESB timestamp
            # not the ts_ref (that comes later)
            if not ts in esb_dict:
                # init usage rec
                esb_rec = {}
                esb_dict[ts] = esb_rec
                esb_rec['ts'] = ts
                esb_rec['ts_ref'] = ts_ref
                esb_rec['dt_ref'] = dt_ref
                esb_rec['import'] = 0
                esb_rec['export'] = 0
            else:
                # retrieve usage rec
                esb_rec = esb_dict[ts]

            # record maximum import/export values encountered 
            # for this period
            # caters for multiple overlapping and contradicting files 
            # but we accept the largest value as the likely valid one

            # FIXME
            # DST winter rollback (yes that little chesnut)
            # the repetition of one hour when the clocks roll back
            # means that this hour is recorded as the larger of two 
            # hours instead of the combination of both
            # messy to try and cater for this while parsing multiple 
            # overlapping files also

            # Import usage
            if hdf_rec['type'] == 'Active Import Interval (kW)':
                esb_rec['import'] = max(esb_rec['import'], float(hdf_rec['value']) / 2)
        
            # Export
            if hdf_rec['type'] == 'Active Export Interval (kW)':
                esb_rec['export'] = max(esb_rec['export'], float(hdf_rec['value']) / 2)

    log_message(
            1,
            'Parsed %d half-hourly records from %s' % (
                len(esb_dict),
                hdf_file_list,
                )
            )

    # merge into hour periods
    # using the common ts_ref we had recorded
    # from the ESB 3-min intervals
    hour_dict = {}

    for ts in esb_dict:
        esb_rec = esb_dict[ts]
        ts_ref = esb_rec['ts_ref']
        dt_ref = esb_rec['dt_ref']

        if not ts_ref in hour_dict:
            hour_dict[ts_ref] = {}
            usage_rec = hour_dict[ts_ref]

            # time fields for the common 
            # hour
            usage_rec['import'] = 0
            usage_rec['export'] = 0
            usage_rec['ts'] = ts_ref
            usage_rec['datetime'] = dt_ref.strftime('%Y/%m/%d %H:%M:%S')

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
            # pull the existing record
            usage_rec = hour_dict[ts_ref]

        # merge the ESB records
        # the same usage rec will be updated by two separate esb
        # records for the 2 30-min periods
        usage_rec['import'] += esb_rec['import']
        usage_rec['export'] += esb_rec['export']

        # align consumed to same import value
        usage_rec['consumed'] = usage_rec['import']

    log_message(
            1,
            'Merged 30-min data into %d hourly records' % (
                len(hour_dict),
                )
            )
    
    # split into separate dicts per day
    day_dict = {}
    for ts in hour_dict:
        usage_rec = hour_dict[ts]
        day = usage_rec['day']
        if not day in day_dict:
            day_dict[day] = {}
    
        day_dict[day][ts] = usage_rec
    
    # Check for full 24h coverage per day
    # purging incomplete days
    purged_day_dict = {}
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
    
        # purge if the tracked hours do not match the expected
        # total. The partial_days option over-rides this
        if (not partial_days and 
            tracked_hours != expected_day_hours):
            del day_dict[day]

            # track the purge context as tracked/expected string
            # in dict
            purge_context = '%d/%d' % (tracked_hours, expected_day_hours)
            purged_day_dict[day] = purge_context
    
    # dump to files
    for day in day_dict:
        # JSONL File
        dest_jsonl_file = '%s/%s.jsonl' % (odir, day)
        log_message(
                1,
                'Writing %s' % (
                    dest_jsonl_file)
                )
        with open(dest_jsonl_file, 'w') as f:
            for key in sorted(day_dict[day].keys()):
                f.write(json.dumps(day_dict[day][key]) + '\n')

    if len(purged_day_dict) > 0:
        log_message(
                1,
                'Purged %d incompete days.. %s' % (
                    len(purged_day_dict),
                    purged_day_dict
                    )
                )


# main()
parser = argparse.ArgumentParser(
        description = 'ESB HDF Reader'
        )

parser.add_argument(
        '--file', 
        help = 'ESB HDF file list', 
        nargs = '+',
        required = True
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory', 
        required = True
        )

parser.add_argument(
        '--timezone', 
        help = 'Timezone', 
        default = 'Europe/Dublin',
        required = False
        )

parser.add_argument(
        '--partial_days', 
        help = 'Include incomplete partial days (skipped by default)', 
        action = 'store_true'
        )

parser.add_argument(
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
hdf_file_list = args['file']
odir = args['odir']
timezone = args['timezone']
partial_days = args['partial_days']
verbose = args['verbose']

# JSON encoder force decimal places to 4
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

process_esb_hdf_files(
        hdf_file_list,
        timezone,
        odir,
        partial_days)
