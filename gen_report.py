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


def add_worksheet(
        workbook,
        sheet_title,
        format_dict,
        field_dict,
        data_dict,
        chart_list = None):

    # nothing to do if no data sent
    if len(data_dict) == 0:
        return

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
                    worksheet.write_datetime(
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

    # Charts
    if not chart_list:
        return

    for chart_rec in chart_list:
        chartsheet = workbook.add_chartsheet(chart_rec['title'])
        chart_def = {
                    'type': chart_rec['type'],
                    }
        if 'sub_type' in chart_rec:
            chart_def['subtype'] = chart_rec['sub_type']
        chart = workbook.add_chart(chart_def)

        chart.set_title({'name': chart_rec['title']})
        chart.set_size({'width': 1920, 'height': 1080})

        x_axis_def = {'name': chart_rec['x_title']}
        if 'x_rotation' in chart_rec:
            x_axis_def['num_font'] = {'rotation' : chart_rec['x_rotation']}
        chart.set_x_axis(x_axis_def)

        y_axis_def = {'name': chart_rec['y_title']}
        if 'y_rotation' in chart_rec:
            y_axis_def['num_font'] = {'rotation' : chart_rec['y_rotation']}
        chart.set_y_axis(y_axis_def)

        if 'style' in chart_rec:
            chart.set_style(chart_rec['style'])

        for series_rec in chart_rec['series']:
            # skip series if the source field is not present
            if not series_rec['field'] in data_field_set:
                continue

            field_rec = field_dict[series_rec['field']]

            series_dict = {
                    'name': [sheet_title, 0, field_rec['col']],
                    'categories': [sheet_title, 1, 0, row, 0],
                    'values': [sheet_title, 1, field_rec['col'], row, field_rec['col']],
                    'line': {'color': series_rec['colour']},
                    }
            chart.add_series(series_dict)
            log_message(
                    0,
                    'Add series %s' % (
                        series_dict)
                    )

        chartsheet.set_chart(chart)

    return


# main()

parser = argparse.ArgumentParser(
        description = 'Energy Data Report Generator'
        )

parser.add_argument(
        '--file', 
        help = 'Output XLSX file', 
        required = True
        )

parser.add_argument(
        '--idir', 
        help = 'Input Directory for data files', 
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
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )


args = vars(parser.parse_args())
report_file_name = args['file']
tariff_list = args['tariff_rate']
interval_list = args['tariff_interval']
fit_rate = args['fit_rate']
idir = args['idir']
start_date = args['start']
end_date = args['end']
timezone = args['timezone']
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

            data_dict[rec['ts']] = rec

            # naive year datetime conversion
            # replaces existing year, month and day fields
            ts_dt = datetime.datetime.strptime(
                    rec['datetime'], 
                    '%Y/%m/%d %H:%M:%S')
            rec['datetime'] = ts_dt

            ## # month and day over-rides with 
            ## # locale-specific text versions
            ## rec['month'] = ts_dt.strftime('%b %Y')
            ## rec['day'] = ts_dt.strftime('%b %d %Y')

            # cost calculation based on hour
            dt_hour = rec['hour']
            rec['import_cost'] = 0
            rec['export_credit'] = 0
            if dt_hour in tarff_interval_dict:
                # calculate as kWh times kWh rate
                rec['tariff_name'] = tarff_interval_dict[dt_hour]
                rec['tariff_rate'] = tariff_dict[rec['tariff_name']]
                rec['import_cost'] = rec['import'] * rec['tariff_rate']

            if fit_rate:
                rec['export_credit'] = rec['export'] * fit_rate

            # relative import/cost
            rec['rel_import'] =  rec['import'] - rec['export']
            rec['rel_cost'] =  rec['import_cost'] - rec['export_credit']

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
str_format.set_num_format('General') # text
str_format.set_align('right')
str_format.set_locked(True) 
format_dict['str'] = str_format

float_format = workbook.add_format() 
# with commas and 3 decimal places
float_format.set_num_format('#,##0.000') 
float_format.set_locked(True) 
format_dict['float'] = float_format

int_format = workbook.add_format() 
# no decimal places
int_format.set_num_format('0') 
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
        'year' : {
            'title' : 'Year',
            'width' : 5,
            'header_format' : 'general',
            'format' : 'str',
            },
        'month' : {
            'title' : 'Month',
            'width' : 9,
            'header_format' : 'general',
            'format' : 'str',
            },
        'day' : {
            'title' : 'Day',
            'width' : 12,
            'header_format' : 'general',
            'format' : 'str',
            },
        'hour' : {
            'title' : 'Hour',
            'width' : 5,
            'header_format' : 'general',
            'format' : 'integer',
            },
        'tariff_name' : {
            'title' : 'Tariff',
            'width' : 12,
            'header_format' : 'general',
            'format' : 'str',
            },
        'tariff_rate' : {
            'title' : 'Rate',
            'width' : 12,
            'header_format' : 'general',
            'format' : 'float',
            },
        'import' : {
            'title' : 'Import (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            'field' : 'import'
            },
        'import_cost' : {
            'title' : 'Import Cost',
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
        'export_credit' : {
            'title' : 'Export Credit',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            },
        'rel_import' : {
            'title' : 'Rel Import (kWh)',
            'width' : 15,
            'header_format' : 'general',
            'format' : 'float',
            'field' : 'import'
            },
        'rel_cost' : {
            'title' : 'Rel Cost',
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
        }

add_worksheet(
        workbook,
        'All',
        format_dict,
        field_dict,
        data_dict)


# aggregate dicts
day_dict = {}
month_dict = {}
year_dict = {}
hour_dict = {}
tariff_dict = {}

for ts in data_dict:
    rec = data_dict[ts]

    hour = rec['hour']
    day = rec['day']
    month = rec['month']
    year = rec['year']

    tariff_name = None
    tariff_rate = None
    if 'tariff_name' in rec:
        tariff_name = rec['tariff_name']
        tariff_rate = rec['tariff_rate']

    if not day in day_dict:
        day_dict[day] = {}
        day_dict[day]['day'] = day
        day_dict[day]['import'] = 0
        day_dict[day]['rel_import'] = 0
        day_dict[day]['export'] = 0
        day_dict[day]['import_cost'] = 0
        day_dict[day]['export_credit'] = 0
        day_dict[day]['rel_cost'] = 0

    if not month in month_dict:
        month_dict[month] = {}
        month_dict[month]['month'] = month
        month_dict[month]['import'] = 0
        month_dict[month]['rel_import'] = 0
        month_dict[month]['export'] = 0
        month_dict[month]['import_cost'] = 0
        month_dict[month]['export_credit'] = 0
        month_dict[month]['rel_cost'] = 0

    if not year in year_dict:
        year_dict[year] = {}
        year_dict[year]['year'] = year
        year_dict[year]['import'] = 0
        year_dict[year]['rel_import'] = 0
        year_dict[year]['export'] = 0
        year_dict[year]['import_cost'] = 0
        year_dict[year]['export_credit'] = 0
        year_dict[year]['rel_cost'] = 0

    if not hour in hour_dict:
        hour_dict[hour] = {}
        hour_dict[hour]['hour'] = hour
        hour_dict[hour]['import'] = 0
        hour_dict[hour]['rel_import'] = 0
        hour_dict[hour]['export'] = 0
        hour_dict[hour]['import_cost'] = 0
        hour_dict[hour]['export_credit'] = 0
        hour_dict[hour]['days'] = 0
        hour_dict[hour]['rel_cost'] = 0

    if tariff_name:
        if not tariff_name in tariff_dict:
            tariff_dict[tariff_name] = {}
            tariff_dict[tariff_name]['tariff_name'] = tariff_name
            tariff_dict[tariff_name]['tariff_rate'] = tariff_rate
            tariff_dict[tariff_name]['import'] = 0
            tariff_dict[tariff_name]['import_cost'] = 0
            tariff_dict[tariff_name]['export'] = 0 
            tariff_dict[tariff_name]['export_credit'] = 0
        tariff_dict[tariff_name]['import'] += rec['import']
        tariff_dict[tariff_name]['import_cost'] += rec['import_cost']

    if fit_rate:
        if not 'FIT' in tariff_dict:
            tariff_dict['FIT'] = {}
            tariff_dict['FIT']['tariff_name'] = 'FIT'
            tariff_dict['FIT']['tariff_rate'] = fit_rate
            tariff_dict['FIT']['import'] = 0
            tariff_dict['FIT']['import_cost'] = 0
            tariff_dict['FIT']['export'] = 0
            tariff_dict['FIT']['export_credit'] = 0

        tariff_dict['FIT']['export'] += rec['export']
        tariff_dict['FIT']['export_credit'] += rec['export_credit']

    day_dict[day]['import'] += rec['import']
    day_dict[day]['rel_import'] += rec['rel_import']
    day_dict[day]['export'] += rec['export']
    day_dict[day]['import_cost'] += rec['import_cost']
    day_dict[day]['export_credit'] += rec['export_credit']
    day_dict[day]['rel_cost'] += rec['rel_cost']

    month_dict[month]['import'] += rec['import']
    month_dict[month]['rel_import'] += rec['rel_import']
    month_dict[month]['export'] += rec['export']
    month_dict[month]['import_cost'] += rec['import_cost']
    month_dict[month]['export_credit'] += rec['export_credit']
    month_dict[month]['rel_cost'] += rec['rel_cost']

    year_dict[year]['import'] += rec['import']
    year_dict[year]['rel_import'] += rec['rel_import']
    year_dict[year]['export'] += rec['export']
    year_dict[year]['import_cost'] += rec['import_cost']
    year_dict[year]['export_credit'] += rec['export_credit']
    year_dict[year]['rel_cost'] += rec['rel_cost']

    hour_dict[hour]['import'] += rec['import']
    hour_dict[hour]['rel_import'] += rec['rel_import']
    hour_dict[hour]['export'] += rec['export']
    hour_dict[hour]['import_cost'] += rec['import_cost']
    hour_dict[hour]['export_credit'] += rec['export_credit']
    hour_dict[hour]['rel_cost'] += rec['rel_cost']
    hour_dict[hour]['days'] += 1

    if 'solar' in rec:
        if not 'solar' in day_dict:
            day_dict[day]['solar'] = 0
            month_dict[month]['solar'] = 0
            year_dict[year]['solar'] = 0
            hour_dict[hour]['solar'] = 0

        day_dict[day]['solar'] += rec['solar']
        month_dict[month]['solar'] += rec['solar']
        year_dict[year]['solar'] += rec['solar']
        hour_dict[hour]['solar'] += rec['solar']

    if 'consumed' in rec:
        if not 'consumed' in day_dict:
            day_dict[day]['consumed'] = 0
            month_dict[month]['consumed'] = 0
            year_dict[year]['consumed'] = 0
            hour_dict[hour]['consumed'] = 0

        day_dict[day]['consumed'] += rec['consumed']
        month_dict[month]['consumed'] += rec['consumed']
        year_dict[year]['consumed'] += rec['consumed']
        hour_dict[hour]['consumed'] += rec['consumed']


add_worksheet(
        workbook,
        'Day',
        format_dict,
        field_dict,
        day_dict,
        chart_list = [
            {
                'title' : 'Day Relative Import',
                'type' : 'column',
                #'sub_type' : 'stacked',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : [
                    {
                        'field': 'rel_import',
                        'colour': 'green'
                        },
                    ]
                },
            {
                'title' : 'Day Relative Cost',
                'type' : 'column',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : [
                    {
                        'field': 'rel_cost',
                        'colour': 'red'
                        },
                    ]
                }
            ]
        )

add_worksheet(
        workbook,
        'Month',
        format_dict,
        field_dict,
        month_dict)

add_worksheet(
        workbook,
        'Year',
        format_dict,
        field_dict,
        year_dict)

add_worksheet(
        workbook,
        '24h',
        format_dict,
        field_dict,
        hour_dict,
        chart_list = [
            {
                'title' : '24h Relative Import',
                'type' : 'column',
                'x_title' : 'Hour',
                'y_title' : 'kWh',
                'series' : [
                    {
                        'field': 'rel_import',
                        'colour': 'green'
                        },
                    ]
                },
            {
                'title' : '24h Relative Cost',
                'type' : 'column',
                'x_title' : 'Hour',
                'y_title' : 'Euro',
                'series' : [
                    {
                        'field': 'rel_cost',
                        'colour': 'green'
                        },
                    ]
                }
            ])

add_worksheet(
        workbook,
        'Tariff',
        format_dict,
        field_dict,
        tariff_dict)

workbook.close()
