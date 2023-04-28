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
    # key list taken from from dict original 
    # construction order
    header_fields = list(field_dict.keys())

    # build set of fields present in data dict
    data_field_set = set()
    for key in data_dict:
        for field in data_dict[key]:
            data_field_set.add(field)

    # remove headers not represented
    # needs to use a 2nd set for this
    header_purge_set = set()
    for field in header_fields:
        if not field in data_field_set:
            header_purge_set.add(field)

    # purge from header list
    for field in header_purge_set:
        header_fields.remove(field)

    # print in-use headers and assign columns
    col = -1
    for field in header_fields:
        col += 1
        field_rec = field_dict[field]
        field_rec['col'] = col
        worksheet.write_string(
                0, 
                field_rec['col'], 
                field_rec['title'], 
                format_dict[field_rec['header_format']])
    
        # column width
        worksheet.set_column(
                field_rec['col'], 
                field_rec['col'], 
                field_rec['width'])
    
    # Freeze top row
    worksheet.freeze_panes(1, 0)

    # data incremental sort on key
    key_list = list(data_dict.keys())
    key_list.sort()
    
    # Populate Rows in sorted order
    row = 0
    for key in key_list:
        rec = data_dict[key]
        row += 1

        for field in header_fields:
            field_rec = field_dict[field]
            if field in rec:
                # write cell
                if field_rec['format'] == 'datetime':
                    value = rec[field]
                    worksheet.write_string(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])

                elif field_rec['format'] == 'str':
                    value = rec[field]
                    worksheet.write_string(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])
    
                elif field_rec['format'] in ['integer', 'float']:
                    value = rec[field]
                    worksheet.write_number(
                            row,
                            field_rec['col'],
                            value,
                            format_dict[field_rec['format']])
                else:
                    # unknown field format
                    # skipped
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

            # cost calculation based on hour
            dt_hour = rec['hour']
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

str_format = workbook.add_format() 
str_format.set_num_format("General") # text
str_format.set_locked(True) # read-only
format_dict['str'] = str_format

float_format = workbook.add_format() 
float_format.set_num_format("#,##0.000") # with commas
float_format.set_locked(True) # read-only
format_dict['float'] = float_format

int_format = workbook.add_format() 
int_format.set_num_format("0") # no decimal places
int_format.set_locked(True) # read-only
format_dict['integer'] = int_format

datetime_format = workbook.add_format() 
datetime_format.set_num_format('yyyy/mm/dd hh:mm:ss')
format_dict['datetime'] = datetime_format

field_dict = {
        'ts' : {
            'title' : 'Timestamp',
            'width' : 20,
            'header_format' : 'general',
            'format' : 'integer',
            },
        'datetime' : {
            'title' : 'Date/Time',
            'width' : 20,
            'header_format' : 'general',
            'format' : 'datetime',
            },
        'import' : {
            'title' : 'Import (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            'field' : 'import'
            },
        'cost' : {
            'title' : 'Cost',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'export' : {
            'title' : 'Export (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'solar' : {
            'title' : 'Solar (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'consumed' : {
            'title' : 'Consumed (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'avg_import' : {
            'title' : 'Avg Import (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'avg_export' : {
            'title' : 'Avg Export (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'avg_solar' : {
            'title' : 'Avg Solar (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'avg_consumed' : {
            'title' : 'Avg Consumed (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'avg_cost' : {
            'title' : 'Avg Cost',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
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

    hour = rec['hour']
    day = rec['day']
    month = rec['month']
    year = rec['year']

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
        day_hour_dict[hour]['datetime'] = hour
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

field_dict['datetime']['format'] = 'str'
field_dict['datetime']['title'] = 'Day'
add_worksheet(
        workbook,
        'Day',
        format_dict,
        field_dict,
        day_dict)

field_dict['datetime']['format'] = 'str'
field_dict['datetime']['title'] = 'Month'
add_worksheet(
        workbook,
        'Month',
        format_dict,
        field_dict,
        month_dict)

field_dict['datetime']['format'] = 'str'
field_dict['datetime']['title'] = 'Year'
add_worksheet(
        workbook,
        'Year',
        format_dict,
        field_dict,
        year_dict)

field_dict['datetime']['format'] = 'integer'
field_dict['datetime']['title'] = 'Hour'
add_worksheet(
        workbook,
        '24h',
        format_dict,
        field_dict,
        day_hour_dict)

workbook.close()
