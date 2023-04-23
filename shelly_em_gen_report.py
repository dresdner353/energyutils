import argparse
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import xlsxwriter


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


def add_worksheet(
        workbook,
        sheet_title,
        format_dict,
        field_dict,
        data_dict):

    log_message(
            1,
            'Adding worksheet %s (%d records)' % (
                sheet_title,
                len(data_dict)
                )
            )
    worksheet = workbook.add_worksheet(sheet_title)

    # Headers
    for field in field_dict:

        field_rec = field_dict[field]
        worksheet.write_string(
                0, 
                field_rec['col'], 
                field,
                format_dict[field_rec['header_format']])
    
        # column width
        worksheet.set_column(
                field_rec['col'], 
                field_rec['col'], 
                field_rec['width'])
    
    # Freeze top row
    worksheet.freeze_panes(1, 0)

    # key sort
    key_list = list(data_dict.keys())
    key_list.sort()
    
    # Rows
    row = 0
    for key in key_list:
        rec = data_dict[key]

        row += 1
        for field in field_dict:

            field_rec = field_dict[field]
            data_field = field_rec['field']
            if data_field in rec:
                # write cell

                if field_rec['format'] in ['datetime', 'day', 'month', 'year', 'hour']:
                    value = rec[data_field]
                    worksheet.write_datetime(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])

                elif field_rec['format'] == 'epoch':
                    value = rec[data_field]
                    if 'conversion' in field_rec:
                        value = eval(field_rec['conversion'])
                    worksheet.write_number(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])

                elif field_rec['format'] == 'text':
                    value = rec[data_field]
                    if 'conversion' in field_rec:
                        value = eval(field_rec['conversion'])
                    worksheet.write_string(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])
    
                elif field_rec['format'] == 'num':
                    value = rec[data_field]
                    if 'conversion' in field_rec:
                        value = eval(field_rec['conversion'])
                    worksheet.write_number(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])
                else:
                    # unknown field format
                    pass
    return



    


# main()

# default storage dir for data
home = os.path.expanduser('~')
default_idir = home + '/.shellyemdata'   

parser = argparse.ArgumentParser(
        description = 'Shelly EM Report Generator'
        )

parser.add_argument(
        '--file', 
        help = 'Output XLSX file', 
        required = True
        )

parser.add_argument(
        '--idir', 
        help = 'Input Directory for data files', 
        default = default_idir,
        required = False
        )

parser.add_argument(
        '--timezone', 
        help = 'Output Timezone', 
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
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )


args = vars(parser.parse_args())
report_file_name = args['file']
timezone = args['timezone']
tariff_list = args['tariff_rate']
interval_list = args['tariff_interval']
idir = args['idir']
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


# load all data
data_dict = {}
file_count = 0
for filename in os.listdir(idir):
    # only loading .jsonl files
    if not filename.endswith(".jsonl"):
        continue

    file_count += 1
    full_path = '%s/%s' % (idir, filename)
    with open(full_path) as fp:
        for line in fp:
            rec = json.loads(line)
            data_dict[rec['ts']] = rec

            # Render epoch ts to UTC datetime
            rec['datetime'] = datetime.datetime.fromtimestamp(rec['ts'])
            # Render to local time zone
            rec['datetime'] = rec['datetime'].astimezone(zoneinfo.ZoneInfo(timezone))
            # strip out timezone (xlsxwriter will not work with it)
            rec['datetime'] = rec['datetime'].replace(tzinfo=None)

            dt_hour = rec['datetime'].hour
            rec['cost'] = 0
            if dt_hour in tarff_interval_dict:
                # calculate as kWh times kWh rate
                rec['tariff_name'] = tarff_interval_dict[dt_hour]
                rec['tariff_rate'] = tariff_dict[rec['tariff_name']]
                rec['cost'] = rec['import'] * rec['tariff_rate']

log_message(
        1,
        'Loaded %d files, %d records' % (
            file_count, 
            len(data_dict)
            )
        )

# XLSX
workbook = xlsxwriter.Workbook(report_file_name)

format_dict = {}

general_label_format = workbook.add_format()
general_label_format.set_text_wrap()
general_label_format.set_bg_color('#C1C1C1')
format_dict['general'] = general_label_format

num_format = workbook.add_format() 
num_format.set_num_format("#,##0.000") # with commas
num_format.set_locked(True) # read-only
format_dict['num'] = num_format

text_format = workbook.add_format({'text_wrap': True}) 
text_format.set_num_format("0") # normal number, no decimal places
text_format.set_locked(True) # read-only
format_dict['text'] = text_format

epoch_format = workbook.add_format({'text_wrap': True}) 
epoch_format.set_num_format("0") # normal number, no decimal places
epoch_format.set_locked(True) # read-only
format_dict['epoch'] = epoch_format

timestamp_format = workbook.add_format() 
timestamp_format.set_num_format('yyyy/mm/dd hh:mm:ss')
format_dict['datetime'] = timestamp_format

hour_format = workbook.add_format() 
hour_format.set_num_format('hh')
format_dict['hour'] = hour_format

day_format = workbook.add_format() 
day_format.set_num_format('yyyy/mm/dd')
format_dict['day'] = day_format

month_format = workbook.add_format() 
month_format.set_num_format('yyyy/mm')
format_dict['month'] = month_format

year_format = workbook.add_format() 
year_format.set_num_format('yyyy')
format_dict['year'] = year_format

field_dict = {
        'Date/Time' : {
            'col' : 0,
            'width' : 20,
            'header_format' : 'general',
            'format' : 'datetime',
            'field' : 'datetime'
            },
        'Hour' : {
            'col' : 0,
            'width' : 20,
            'header_format' : 'general',
            'format' : 'hour',
            'field' : 'hour'
            },
        'Import (kWh)' : {
            'col' : 1,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'import'
            },
        'Cost' : {
            'col' : 2,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'cost',
            },
        'Export (kWh)' : {
            'col' : 3,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'export',
            },
        'Solar (kWh)' : {
            'col' : 4,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'solar',
            },
        'Consumed (kWh)' : {
            'col' : 5,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'consumed',
            },
        'Avg Import (kWh)' : {
            'col' : 6,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'avg_import',
            },
        'Avg Export (kWh)' : {
            'col' : 7,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'avg_export',
            },
        'Avg Solar (kWh)' : {
            'col' : 8,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'avg_solar',
            },
        'Avg Consumed (kWh)' : {
            'col' : 9,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'avg_consumed',
            },
        'Avg Cost' : {
            'col' : 10,
            'width' : 15,
            'header_format' : 'general',
            'format' : 'num',
            'field' : 'avg_cost',
            },

        }

add_worksheet(
        workbook,
        'Hour',
        format_dict,
        field_dict,
        data_dict)


# aggregate dicts
day_dict = {}
month_dict = {}
year_dict = {}
day_hour_dict = {}

for ts in data_dict:
    rec = data_dict[ts]
    dt = rec['datetime']

    # round datetimes to specific day, month or year
    day = dt.replace(
            hour = 0,
            minute = 0,
            second = 0,
            microsecond = 0
            )

    month = dt.replace(
                day = 1,
                hour = 0,
                minute = 0,
                second = 0,
                microsecond = 0)

    year = dt.replace(
            month = 1,
            day = 1,
            hour = 0,
            minute = 0,
            second = 0,
            microsecond = 0
            )

    hour = dt.hour

    if not day in day_dict:
        day_dict[day] = {}
        day_dict[day]['datetime'] = day
        day_dict[day]['import'] = 0
        day_dict[day]['export'] = 0
        day_dict[day]['solar'] = 0
        day_dict[day]['consumed'] = 0
        day_dict[day]['cost'] = 0

    if not month in month_dict:
        month_dict[month] = {}
        month_dict[month]['datetime'] = month
        month_dict[month]['import'] = 0
        month_dict[month]['export'] = 0
        month_dict[month]['solar'] = 0
        month_dict[month]['consumed'] = 0
        month_dict[month]['cost'] = 0

    if not year in year_dict:
        year_dict[year] = {}
        year_dict[year]['datetime'] = year
        year_dict[year]['import'] = 0
        year_dict[year]['export'] = 0
        year_dict[year]['solar'] = 0
        year_dict[year]['consumed'] = 0
        year_dict[year]['cost'] = 0

    if not hour in day_hour_dict:
        day_hour_dict[hour] = {}
        day_hour_dict[hour]['hour'] = dt
        day_hour_dict[hour]['import'] = 0
        day_hour_dict[hour]['export'] = 0
        day_hour_dict[hour]['solar'] = 0
        day_hour_dict[hour]['consumed'] = 0
        day_hour_dict[hour]['cost'] = 0
        day_hour_dict[hour]['days'] = 0

    day_dict[day]['import'] += rec['import']
    day_dict[day]['export'] += rec['export']
    day_dict[day]['solar'] += rec['solar']
    day_dict[day]['consumed'] += rec['consumed']
    day_dict[day]['cost'] += rec['cost']

    month_dict[month]['import'] += rec['import']
    month_dict[month]['export'] += rec['export']
    month_dict[month]['solar'] += rec['solar']
    month_dict[month]['consumed'] += rec['consumed']
    month_dict[month]['cost'] += rec['cost']

    year_dict[year]['import'] += rec['import']
    year_dict[year]['export'] += rec['export']
    year_dict[year]['solar'] += rec['solar']
    year_dict[year]['consumed'] += rec['consumed']
    year_dict[year]['cost'] += rec['cost']

    day_hour_dict[hour]['import'] += rec['import']
    day_hour_dict[hour]['export'] += rec['export']
    day_hour_dict[hour]['solar'] += rec['solar']
    day_hour_dict[hour]['consumed'] += rec['consumed']
    day_hour_dict[hour]['cost'] += rec['cost']
    day_hour_dict[hour]['days'] += 1
    day_hour_dict[hour]['avg_import'] = day_hour_dict[hour]['import'] / day_hour_dict[hour]['days']
    day_hour_dict[hour]['avg_export'] = day_hour_dict[hour]['export'] / day_hour_dict[hour]['days']
    day_hour_dict[hour]['avg_solar'] = day_hour_dict[hour]['solar'] / day_hour_dict[hour]['days']
    day_hour_dict[hour]['avg_consumed'] = day_hour_dict[hour]['consumed'] / day_hour_dict[hour]['days']
    day_hour_dict[hour]['avg_cost'] = day_hour_dict[hour]['cost'] / day_hour_dict[hour]['days']

field_dict['Date/Time']['format'] = 'day'
add_worksheet(
        workbook,
        'Day',
        format_dict,
        field_dict,
        day_dict)

field_dict['Date/Time']['format'] = 'month'
add_worksheet(
        workbook,
        'Month',
        format_dict,
        field_dict,
        month_dict)

field_dict['Date/Time']['format'] = 'year'
add_worksheet(
        workbook,
        'Year',
        format_dict,
        field_dict,
        year_dict)

field_dict['Date/Time']['format'] = 'hour'
add_worksheet(
        workbook,
        '24h',
        format_dict,
        field_dict,
        day_hour_dict)

workbook.close()
