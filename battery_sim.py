import argparse
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


def load_data(
        idir,
        start_date,
        end_date,
        timezone):

    global verbose

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

    # load all data
    data_dict = {}
    file_count = 0
    for filename in os.listdir(idir):
        # only loading .jsonl files
        if not filename.endswith('.jsonl'):
            continue
    
        file_count += 1
        full_path = '%s/%s' % (idir, filename)
        with open(full_path) as fp:
            for line in fp:
                rec = json.loads(line)
    
                # skip records if out of range
                # FIXME probably could also include skipping of 
                # full files based on name
                if (start_ts and 
                    rec['ts'] < start_ts):
                    continue
    
                if (end_ts and 
                    rec['ts'] > end_ts):
                    continue
    
                # store keyed on ts
                data_dict[rec['ts']] = rec
    
    log_message(
            1,
            'Loaded %d files, %d records' % (
                file_count, 
                len(data_dict)
                )
            )

    return data_dict


def output_results(
        odir,
        data_dict,
        prefix,
        decimal_places):

    # no date, nothing to do
    if len(data_dict) == 0:
        return

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

    return


def gen_time_interval_set(
        interval_range):

    interval_set = set()

    if interval_range:
        fields = interval_range.split('-')
        start_hh = int(fields[0])
        end_hh = int(fields[1])
        
        if start_hh == end_hh:
            # single xx:xx range (full 24 hours)
            for i in range(0, 24):
                interval_set.add(i)
        else:
            hh = start_hh
            while hh != end_hh:
                interval_set.add(hh)
                hh = (hh + 1) % 24

    return interval_set


# main()

parser = argparse.ArgumentParser(
        description = 'Battery Simulator'
        )

parser.add_argument(
        '--idir', 
        help = 'Input Directory for data files', 
        required = True
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory for modifled data files', 
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
        '--battery_capacity', 
        help = 'Battery Capacity (kWh)', 
        type = float,
        required = True
        )

parser.add_argument(
        '--max_charge_percent', 
        help = 'Battery Max Charge Percentage (1..100)', 
        type = int,
        choices = range(1, 101),
        required = True
        )

parser.add_argument(
        '--min_charge_percent', 
        help = 'Battery Min Charge Percentage (1..100)', 
        type = int,
        choices = range(1, 101),
        required = True
        )

parser.add_argument(
        '--charge_rate', 
        help = 'Battery Charge Rate (kWh/hour)', 
        type = float,
        required = True
        )

parser.add_argument(
        '--discharge_rate', 
        help = 'Battery Discharge Rate (kWh/hour)', 
        type = float,
        required = True
        )

parser.add_argument(
        '--charge_loss_percent', 
        help = 'Charge Loss Percentage (1..100) def:10', 
        type = int,
        choices = range(0, 101),
        default = 10,
        required = False
        )

parser.add_argument(
        '--discharge_bypass_interval', 
        help = 'Time Interval for Discharge Bypass <HH-HH>', 
        required = False,
        default = None
        )

parser.add_argument(
        '--grid_shift_interval', 
        help = 'Time Interval for Grid Charging <HH-HH>', 
        required = False,
        default = None
        )

parser.add_argument(
        '--fit_discharge_interval', 
        help = 'Time Interval for FIT discharge <HH-HH>', 
        required = False,
        default = None
        )

parser.add_argument(
        '--export_charge_boundary', 
        help = 'Min Export required for charging (kWh/hour)', 
        type = float,
        default = 0.05,
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
idir = args['idir']
odir = args['odir']
start_date = args['start']
end_date = args['end']
timezone = args['timezone']
battery_capacity = args['battery_capacity']
max_charge_percent = args['max_charge_percent']
min_charge_percent = args['min_charge_percent']
charge_rate = args['charge_rate']
discharge_rate = args['discharge_rate']
charge_loss_percent = args['charge_loss_percent']
discharge_bypass_interval = args['discharge_bypass_interval']
grid_shift_interval = args['grid_shift_interval']
fit_discharge_interval = args['fit_discharge_interval']
export_charge_boundary = args['export_charge_boundary']
decimal_places = args['decimal_places']
verbose = args['verbose']

data_dict = load_data(
        idir,
        start_date,
        end_date,
        timezone)

discharge_bypass_set = gen_time_interval_set(discharge_bypass_interval)
grid_shift_set = gen_time_interval_set(grid_shift_interval)
fit_discharge_set = gen_time_interval_set(fit_discharge_interval)

current_battery_storage = 0
overall_charge_total = 0
overall_discharge_total = 0

# factor to convert battery storage into the equivalent
# of grid or solar draw
# we multiple what we want to store in the battery by this value
battery_to_ac_factor = 1 + (charge_loss_percent / 100)
ac_to_battery_factor = (100 - charge_loss_percent) / 100 

max_charge_capacity = battery_capacity * max_charge_percent/100

# scan data to simulate battery
key_list = list(data_dict.keys())
key_list.sort()

for key in key_list:
    rec = data_dict[key]

    # solar charge only applies when export reaches min boundary
    # helps avoid invalid phantom charges overnight
    solar_charge_amount = 0
    if rec['export'] >= export_charge_boundary:
        # determine how much storage space we have 
        available_charge_capacity = max_charge_capacity - current_battery_storage

        # determine what can be charged
        # the min of charge rate and available capacity
        max_charge_amount = min(available_charge_capacity, charge_rate)

        # loss conversions
        adjusted_charge_amount = max_charge_amount * battery_to_ac_factor
        solar_divert_amount = min(rec['export'], adjusted_charge_amount)
        solar_charge_amount = solar_divert_amount * ac_to_battery_factor

        # Reduce export and charge battery
        current_battery_storage += solar_charge_amount
        rec['export'] -= solar_divert_amount
        overall_charge_total += solar_charge_amount

    # grid shift charge
    grid_charge_amount = 0
    if rec['hour'] in grid_shift_set:
        # determine how much storage space we have 
        available_charge_capacity = max_charge_capacity - current_battery_storage

        # determine what can be charged
        # the min of charge rate and available capacity
        max_charge_amount = min(available_charge_capacity, charge_rate)

        # loss conversions
        adjusted_charge_amount = max_charge_amount * battery_to_ac_factor

        # charge battery from grid
        grid_charge_amount = max_charge_amount
        current_battery_storage += grid_charge_amount
        rec['import'] += adjusted_charge_amount
        rec['consumed'] = rec['import']
        overall_charge_total += grid_charge_amount

    # discharge is conditional to time of day
    discharge_amount = 0
    if not rec['hour'] in discharge_bypass_set:
        # determine how much charge we have to use
        available_discharge_capacity = current_battery_storage - (battery_capacity * min_charge_percent/100)
        if available_discharge_capacity < 0:
            available_discharge_capacity = 0

        # determine discharge
        max_discharge_amount = min(available_discharge_capacity, discharge_rate)

        # determine actual charge amount
        discharge_amount = min(rec['import'], max_discharge_amount)

        # Discharge battery and Reduce import 
        current_battery_storage -= discharge_amount
        rec['import'] -= discharge_amount
        rec['consumed'] = rec['import']
        overall_discharge_total += discharge_amount

    # FIT discharge 
    if rec['hour'] in fit_discharge_set:
        # determine how much charge we have to use
        available_discharge_capacity = current_battery_storage - (battery_capacity * min_charge_percent/100)
        if available_discharge_capacity < 0:
            available_discharge_capacity = 0

        # determine discharge
        max_discharge_amount = min(available_discharge_capacity, discharge_rate)

        # Discharge battery and increase export
        current_battery_storage -= max_discharge_amount
        rec['export'] += max_discharge_amount
        overall_discharge_total += max_discharge_amount

    # record activity and charge status in record
    rec['battery_solar_charge'] = solar_charge_amount
    rec['battery_grid_charge'] = grid_charge_amount
    rec['battery_discharge'] = discharge_amount
    rec['battery_storage'] = current_battery_storage
    rec['battery_capacity'] = round(current_battery_storage / battery_capacity * 100)

    log_message(
            verbose,
            '%s charge:+%.2fkWh discharge:-%.2fkWh batt:%.2fkWh (%d%%)' % (
                rec['datetime'],
                solar_charge_amount + grid_charge_amount,
                rec['battery_discharge'],
                rec['battery_storage'],
                rec['battery_capacity']
                )
            )

# split into separate dicts per day
day_dict = {}
for ts in data_dict:
    usage_rec = data_dict[ts]
    day = usage_rec['day']
    if not day in day_dict:
        day_dict[day] = {}

    day_dict[day][ts] = usage_rec

# JSON encoder force decimal places to 4
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.4f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

for day in sorted(day_dict.keys()):
    output_results(
            odir,
            day_dict[day],
            day,
            decimal_places)   


# determine total charge cycles to date
charge_cycles = overall_charge_total / (battery_capacity * max_charge_percent/100)

log_message(
        1,
        'Final battery state.. charge:%.2fkWh (%d%%) ovl_charge:%.2fkWh (%d cycles) ovl_discharge:%.2fkWh' % (
            current_battery_storage,
            round(current_battery_storage / battery_capacity * 100),
            overall_charge_total,
            charge_cycles,
            overall_discharge_total
            )
        )
