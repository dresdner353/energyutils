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
        help = 'Charge Loss Percentage (1..100) def:7', 
        type = int,
        choices = range(0, 101),
        default = 7,
        required = False
        )

parser.add_argument(
        '--discharge_loss_percent', 
        help = 'Discharge Loss Percentage (1..100) def:7', 
        type = int,
        choices = range(0, 101),
        default = 7,
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
discharge_loss_percent = args['discharge_loss_percent']
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
overall_battery_cycles = 0

# charging factors
battery_to_ac_charge_factor = 1 + (charge_loss_percent / 100)
ac_to_battery_charge_factor = (100 - charge_loss_percent) / 100 

# discharging factors
battery_to_ac_discharge_factor = (100 - discharge_loss_percent) / 100
ac_to_battery_discharge_factor = 1 + (discharge_loss_percent / 100)

max_charge_capacity = battery_capacity * max_charge_percent/100

# scan data to simulate battery
key_list = list(data_dict.keys())
key_list.sort()

for key in key_list:
    rec = data_dict[key]

    # solar charge only applies when export reaches min boundary
    # helps avoid invalid phantom charges overnight
    battery_solar_charge = 0
    if rec['export'] >= export_charge_boundary:
        # determine how much storage space we have 
        available_charge_capacity = max_charge_capacity - current_battery_storage

        # determine what can be charged
        # the min of charge rate and available capacity
        max_export_charge = min(available_charge_capacity, charge_rate)

        # charge loss conversions
        ac_charge = max_export_charge * battery_to_ac_charge_factor
        solar_export_divert = min(rec['export'], ac_charge)
        battery_solar_charge = solar_export_divert * ac_to_battery_charge_factor

        log_message(
                verbose,
                '[%s] export charge:.. exp:%.4f max:%.4f exp_div:%.4f bat_chg:%.4f' % (
                    rec['datetime'],
                    rec['export'],
                    max_export_charge,
                    solar_export_divert,
                    battery_solar_charge
                    )
                )

        # Reduce export and charge battery
        current_battery_storage += battery_solar_charge
        rec['export'] -= solar_export_divert
        overall_charge_total += battery_solar_charge

    # grid shift charge
    battery_grid_shift_charge = 0
    if rec['hour'] in grid_shift_set:
        # determine how much storage space we have 
        available_charge_capacity = max_charge_capacity - current_battery_storage

        # determine what can be charged
        # the min of charge rate and available capacity
        battery_grid_shift_charge = min(available_charge_capacity, charge_rate)

        # charge loss conversions
        import_grid_shift_charge = battery_grid_shift_charge * battery_to_ac_charge_factor

        log_message(
                verbose,
                '[%s] grid charge:.. bat_chg:%.4f imp_chg:%.4f' % (
                    rec['datetime'],
                    battery_grid_shift_charge,
                    import_grid_shift_charge,
                    )
                )

        # charge battery from grid
        current_battery_storage += battery_grid_shift_charge
        rec['import'] += import_grid_shift_charge
        rec['consumed'] = rec['import']
        overall_charge_total += battery_grid_shift_charge

    # discharge is conditional to 
    # grid shift and discharge bypass times
    import_discharge = 0
    export_discharge = 0
    battery_import_discharge = 0
    battery_fit_discharge = 0
    if (not rec['hour'] in discharge_bypass_set and 
        not rec['hour'] in grid_shift_set):
        # determine how much charge we have to use
        available_discharge_capacity = current_battery_storage - (battery_capacity * min_charge_percent/100)
        if available_discharge_capacity < 0:
            available_discharge_capacity = 0

        # determine max discharge
        max_discharge = min(available_discharge_capacity, discharge_rate)

        # discharge loss conversions
        ac_discharge = max_discharge * battery_to_ac_discharge_factor
        import_discharge = min(rec['import'], ac_discharge)
        battery_import_discharge = import_discharge * ac_to_battery_discharge_factor

        log_message(
                verbose,
                '[%s] import discharge:.. imp:%.4f max:%.4f imp_dis:%.4f bat_dis:%.4f' % (
                    rec['datetime'],
                    rec['import'],
                    max_discharge,
                    import_discharge,
                    battery_import_discharge
                    )
                )

        # Discharge battery and reduce import 
        current_battery_storage -= battery_import_discharge
        rec['import'] -= import_discharge
        rec['consumed'] = rec['import']
        overall_discharge_total += battery_import_discharge

        # Forced FIT discharge 
        # trying to flush the battery to the grid
        battery_fit_discharge = 0
        if rec['hour'] in fit_discharge_set:
            # determine additional discharge possible
            # taking off any existing import discharge we had applied
            battery_fit_discharge = max_discharge - battery_import_discharge
            export_discharge = battery_fit_discharge * battery_to_ac_discharge_factor

            log_message(
                    verbose,
                    '[%s] fit discharge:.. exp_dis:%.4f bat_dis:%.4f' % (
                        rec['datetime'],
                        export_discharge,
                        battery_fit_discharge
                        )
                    )

            # Additionally discharge battery to max and increase export
            current_battery_storage -= battery_fit_discharge
            rec['export'] += export_discharge
            overall_discharge_total += battery_fit_discharge

    # record activity and charge status in record
    rec['battery_solar_charge'] = battery_solar_charge
    rec['battery_grid_charge'] = battery_grid_shift_charge
    rec['battery_discharge'] = battery_import_discharge + battery_fit_discharge
    rec['battery_storage'] = current_battery_storage
    rec['battery_capacity'] = round(current_battery_storage / battery_capacity * 100)
    total_charge_discharge = battery_solar_charge + battery_grid_shift_charge + import_discharge + battery_fit_discharge
    rec['battery_cycles'] = total_charge_discharge / (max_charge_capacity * 2)
    overall_battery_cycles += rec['battery_cycles']


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


log_message(
        1,
        'Final battery state.. charge:%.4fkWh (%d%%) ovl_charge:%.4fkWh ovl_discharge:%.4fkWh (%d cycles)' % (
            current_battery_storage,
            round(current_battery_storage / battery_capacity * 100),
            overall_charge_total,
            overall_discharge_total,
            overall_battery_cycles,
            )
        )
