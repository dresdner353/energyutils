import argparse
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import sys
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

    global verbose

    # nothing to do if no data sent
    if len(data_dict) == 0:
        return

    log_message(
            1,
            'Adding worksheet %s (%d rows)' % (
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
    
    # Freeze top row and 
    # set height to 2 rows
    worksheet.freeze_panes(1, 0)
    worksheet.set_row(0, 30)

    # Enable Auto Filter across all columns
    worksheet.autofilter(0, 0, 0, len(header_fields) - 1)  

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
            # write string
            if field_rec['format'] == 'str':
                # use present value or empty string
                if field in rec:
                    value = rec[field]
                else:
                    value = ''

                worksheet.write_string(
                        row,
                        field_rec['col'],
                        value,
                        format_dict[field_rec['format']])
    
            # write number
            elif field_rec['format'] in ['integer', 'float']:
                if field in rec:
                    value = rec[field]
                else:
                    value = 0

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

        series_added = 0
        for series_rec in chart_rec['series']:
            # skip series if the source field is not present
            if not series_rec['field'] in data_field_set:
                continue

            field_rec = field_dict[series_rec['field']]

            series_dict = {
                    'name': [sheet_title, 0, field_rec['col']],
                    'categories': [sheet_title, 1, 0, row, 0],
                    'values': [sheet_title, 1, field_rec['col'], row, field_rec['col']],
                    }
            # optional series colour
            if 'colour' in series_rec:
                series_dict['line'] = {'color': series_rec['colour']}
                series_dict['fill'] = {'color': series_rec['colour']}
                series_dict['border'] = {'color': series_rec['colour']}

            if 'negative_colour' in series_rec:
                series_dict['invert_if_negative'] = True
                series_dict['invert_if_negative_color'] = series_rec['negative_colour']

            chart.add_series(series_dict)
            series_added += 1

        # only add the chart and sheet if it has 1+ series
        # added
        if series_added > 0:
            chartsheet = workbook.add_chartsheet(chart_rec['title'])
            chartsheet.set_chart(chart)

    return


def gen_aggregate_dict(
        data_dict,
        agg_field):

    agg_dict = {}

    # skipped fields
    # some special cases and the aggregate 
    # itself
    field_skip_list = [
            'ts', 
            'hour',
            'tariff_rate',
            'export_rate',
            ]
    field_skip_list.append(agg_field)

    for ts in data_dict:
        rec = data_dict[ts]

        # skip records that do not have 
        # the aggregate field
        if not agg_field in rec:
            continue

        agg_value = rec[agg_field]

        # initialise aggregate record
        if not agg_value in agg_dict:
            agg_dict[agg_value] = {}
            agg_dict[agg_value][agg_field] = agg_value

        # aggregate field values
        for field in rec:
            # skip certain fields
            if field in field_skip_list:
                continue

            # skip any non-number fields
            if not type(rec[field]) in [int, float]:
                continue

            # set to value on first encounter or 
            # add to existing aggregate total
            if not field in agg_dict[agg_value]:
                agg_dict[agg_value][field] = rec[field]
            else:
                agg_dict[agg_value][field] += rec[field]

    return agg_dict


def load_data(
        idir,
        start_date,
        end_date,
        standing_rate,
        tariff_list,
        interval_list,
        fit_rate):

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

            # D-D:HH-HH:Tariff_Name
            # First Day range is optional
            fields = interval_str.split(':')

            if len(fields) == 2:
                # no day range specified
                hour_fields = fields[0].split('-')
                start_hh = int(hour_fields[0])
                end_hh = int(hour_fields[1])
                tariff_name = fields[1]
                days = [1,2,3,4,5,6,7]

            elif len(fields) == 3:
                # day range specified
                day_fields = fields[0].split('-')
                start_day = int(day_fields[0])
                end_day = int(day_fields[1])

                # populate days list from specified range
                days = []
                for day in range(1, 8):
                    if (day >= start_day and 
                        day <= end_day):
                        days.append(day)

                hour_fields = fields[1].split('-')
                start_hh = int(hour_fields[0])
                end_hh = int(hour_fields[1])
                tariff_name = fields[2]

            else:
                # ignore mal-formed entries
                # FIXME needs more advanced error handling
                continue

            for day in days:
                # Initialise day
                if not day in tarff_interval_dict:
                    tarff_interval_dict[day] = {}

                if start_hh == end_hh:
                    # single xx:xx range (full 24 hours)
                    for i in range(0, 24):
                        tarff_interval_dict[day][i] = tariff_name
                else:
                    hh = start_hh
                    while hh != end_hh:
                        if tariff_name in tariff_dict:
                            tarff_interval_dict[day][hh] = tariff_name
                            hh = (hh + 1) % 24
        log_message(
                verbose,
                'Tariff Intervals: %s' % (
                    json.dumps(
                        tarff_interval_dict, 
                        indent = 4)
                    )
                )
    
        for day in [1,2,3,4,5,6,7]:
            if not day in tarff_interval_dict:
                log_message(
                        1,
                        'WARNING: Tariff interval data not present for day %d' % (
                            day)   
                        )
        for day in tarff_interval_dict.keys():
            if len(tarff_interval_dict[day]) != 24:
                log_message(
                        1,
                        'WARNING: Tariff interval data present for only %d/24 hours in day %d' % (
                            len(tarff_interval_dict[day]),
                            day)   
                        )

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
    
                # naive datetime conversion
                # into datetime object
                datetime_dt = datetime.datetime.strptime(
                        rec['datetime'], 
                        '%Y/%m/%d %H:%M:%S')
                # reformat back to YYYY-MM-DD HH
                # to reduce to the hour it represents
                rec['datetime'] = datetime_dt.strftime('%Y-%m-%d %H')
    
                # store keyed on datetime object
                data_dict[rec['datetime']] = rec
    
                # cost calculation based on week day number and hour
                # weekday is formatted as '<num> <local name>'
                # so we plit on whitespace and get int() of first field
                dt_weekday = int(rec['weekday'].split(' ')[0])
                dt_hour = rec['hour']

                # relative import
                # initial calc is import - export
                rec['rel_import'] =  rec['import'] - rec['export'] 
    
                # Import Tariff and charging rates
                if (dt_weekday in tarff_interval_dict and 
                    dt_hour in tarff_interval_dict[dt_weekday]):
                    rec['tariff_name'] = tarff_interval_dict[dt_weekday][dt_hour]
                    rec['tariff_rate'] = tariff_dict[rec['tariff_name']]
                    rec['import_cost'] = rec['import'] * rec['tariff_rate']
                    rec['rel_cost'] = rec['import_cost']

                    if standing_rate:
                        rec['standing_cost'] = standing_rate
                        rec['rel_cost'] += rec['standing_cost']

                    # FIT (export_credit)
                    # calculates the credit and export and 
                    # adjusts relative cost to match
                    if fit_rate:
                        rec['export_rate'] = fit_rate
                        rec['export_credit'] = rec['export'] * fit_rate
                        rec['rel_cost'] -= rec['export_credit'] 

                    # Solar credit (saving) based on consumed units against
                    # effective import tariff
                    # Also reduces relative import and cost accordingly
                    if 'solar_consumed' in rec:
                        rec['solar_credit'] = rec['solar_consumed'] * rec['tariff_rate']
                        rec['rel_import'] -= rec['solar_consumed']
                        rec['rel_cost'] -= rec['solar_credit']
    
    log_message(
            1,
            'Loaded %d files, %d records' % (
                file_count, 
                len(data_dict)
                )
            )

    return data_dict


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
        help = 'Time Interval for Tariff <[D-D:]HH-HH:Tariff Name> <[D-D:]HH-HH:Tariff Name> ...', 
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
        '--standing_rate', 
        help = 'Standing Charge (cost per hour)', 
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
standing_rate = args['standing_rate']
idir = args['idir']
start_date = args['start']
end_date = args['end']
timezone = args['timezone']
verbose = args['verbose']

log_message(
        1,
        'Generating report %s' % (
            report_file_name
            )
        )

data_dict = load_data(
        idir,
        start_date,
        end_date,
        standing_rate,
        tariff_list,
        interval_list,
        fit_rate)

# XLSX
workbook = xlsxwriter.Workbook(report_file_name)

# try to reconstruct the command line 
# options to capture in the properties
cmdline_str = 'Invoke options:\n'
for arg in sys.argv:
    if arg.startswith('--'):
        cmdline_str += '\n'
    cmdline_str += ' ' + arg

workbook.set_properties(
    {
        'title': 'Energy Usage Report',
        'subject': 'Python-generated Excel report based on energy usage data',
        'keywords': 'python energy solar report',
        'author': 'https://github.com/dresdner353/energyutils',
        'comments': cmdline_str
    }
)

format_dict = {}

header_format = workbook.add_format()
header_format.set_text_wrap()
header_format.set_align('top')
header_format.set_align('center')
header_format.set_bg_color('#C1C1C1')
format_dict['header'] = header_format

str_format = workbook.add_format() 
str_format.set_num_format('General') # text
str_format.set_align('right')
format_dict['str'] = str_format

float_format = workbook.add_format() 
# with commas and 4 decimal places
float_format.set_num_format('#,##0.0000') 
format_dict['float'] = float_format

int_format = workbook.add_format() 
# no decimal places
int_format.set_num_format('0') 
format_dict['integer'] = int_format

field_dict = {
        'datetime' : {
            'title' : 'Date',
            'width' : 20,
            'header_format' : 'header',
            'format' : 'str',
            },
        'ts' : {
            'title' : 'Epoch',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'integer',
            },
        'year' : {
            'title' : 'Year',
            'width' : 5,
            'header_format' : 'header',
            'format' : 'str',
            },
        'month' : {
            'title' : 'Month',
            'width' : 8,
            'header_format' : 'header',
            'format' : 'str',
            },
        'week' : {
            'title' : 'Week',
            'width' : 8,
            'header_format' : 'header',
            'format' : 'str',
            },
        'day' : {
            'title' : 'Day',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'str',
            },
        'weekday' : {
            'title' : 'Weekday',
            'width' : 8,
            'header_format' : 'header',
            'format' : 'str',
            },
        'hour' : {
            'title' : 'Hour',
            'width' : 5,
            'header_format' : 'header',
            'format' : 'integer',
            },

        'tariff_name' : {
            'title' : 'Import Tariff',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'str',
            },
        'tariff_rate' : {
            'title' : 'Import Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'float',
            },

        'standing_cost' : {
            'title' : 'Standing Cost',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'float',
            },

        'import' : {
            'title' : 'Import (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            'field' : 'import'
            },
        'import_cost' : {
            'title' : 'Import Cost',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },

        'solar' : {
            'title' : 'Solar Generation (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },
        'solar_consumed' : {
            'title' : 'Solar Consumed (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },
        'solar_credit' : {
            'title' : 'Solar Credit',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },
        'export_rate' : {
            'title' : 'Export Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'float',
            },
        'export' : {
            'title' : 'Export (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },
        'export_credit' : {
            'title' : 'Export Credit',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },

        'consumed' : {
            'title' : 'Consumed (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },

        'rel_import' : {
            'title' : 'Rel Import (kWh)',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            'field' : 'import'
            },
        'rel_cost' : {
            'title' : 'Rel Cost',
            'width' : 15,
            'header_format' : 'header',
            'format' : 'float',
            },
        }


# aggregate dicts
day_dict = gen_aggregate_dict(data_dict, 'day')
weekday_dict = gen_aggregate_dict(data_dict, 'weekday')
week_dict = gen_aggregate_dict(data_dict, 'week')
month_dict = gen_aggregate_dict(data_dict, 'month')
year_dict = gen_aggregate_dict(data_dict, 'year')
hour_dict = gen_aggregate_dict(data_dict, 'hour')
tariff_dict = gen_aggregate_dict(data_dict, 'tariff_name')

# Aggregate worksheets
consumption_series =  [
        {
            'field': 'import',
            'colour': 'red',
            },
        {
            'field': 'solar_consumed',
            'colour': 'green',
            },
        ]

import_series =  [
        {
            'field': 'solar',
            'colour': 'green',
            },
        {
            'field': 'rel_import',
            'colour': 'blue',
            },
        ]

full_cost_series = [
        {
            'field': 'import_cost',
            'colour': 'red',
            },
        {
            'field': 'solar_credit',
            'colour': 'green',
            },
        {
            'field': 'export_credit',
            'colour': 'blue',
            },
        ]

rel_cost_series = [
        {
            'field': 'rel_cost',
            'colour': 'green',
            },
        ]

tariff_cost_series = [
        {
            'field': 'import_cost',
            'colour': 'red',
            },
        {
            'field': 'solar_credit',
            'colour': 'green',
            },
        {
            'field': 'export_credit',
            'colour': 'blue',
            },
        ]


add_worksheet(
        workbook,
        'Hour',
        format_dict,
        field_dict,
        data_dict,
        chart_list = [
            {
                'title' : 'Hourly Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : consumption_series,
                },
            {
                'title' : 'Hourly Import',
                'type' : 'column',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Hourly Cost',
                'type' : 'column',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : 'Hourly Relative Cost',
                'type' : 'column',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ]
        )


add_worksheet(
        workbook,
        'Day',
        format_dict,
        field_dict,
        day_dict,
        chart_list = [
            {
                'title' : 'Daily Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : consumption_series,
                },
            {
                'title' : 'Daily Import',
                'type' : 'column',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Daily Cost',
                'type' : 'column',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : 'Daily Relative Cost',
                'type' : 'column',
                'x_title' : 'Day',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ]
        )

add_worksheet(
        workbook,
        'Week',
        format_dict,
        field_dict,
        week_dict,
        chart_list = [
            {
                'title' : 'Weekly Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Week',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : consumption_series,
                },
            {
                'title' : 'Weekly Import',
                'type' : 'column',
                'x_title' : 'Week',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Weekly Cost',
                'type' : 'column',
                'x_title' : 'Week',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : 'Weekly Relative Cost',
                'type' : 'column',
                'x_title' : 'Week',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ]
        )

add_worksheet(
        workbook,
        'Month',
        format_dict,
        field_dict,
        month_dict,
        chart_list = [
            {
                'title' : 'Monthly Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Month',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : consumption_series,
                },
            {
                'title' : 'Monthly Import',
                'type' : 'column',
                'x_title' : 'Month',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Monthly Cost',
                'type' : 'column',
                'x_title' : 'Month',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : 'Monthly Relative Cost',
                'type' : 'column',
                'x_title' : 'Month',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ]
        )

add_worksheet(
        workbook,
        'Year',
        format_dict,
        field_dict,
        year_dict)

add_worksheet(
        workbook,
        'Weekday',
        format_dict,
        field_dict,
        weekday_dict,
        chart_list = [
            {
                'title' : 'Weekday Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Weekday',
                'y_title' : 'kWh',
                'series' : consumption_series
                },
            {
                'title' : 'Weekday Import',
                'type' : 'column',
                'x_title' : 'Weekday',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Weekday Cost',
                'type' : 'column',
                'x_title' : 'Weekday',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : 'Weekday Relative Cost',
                'type' : 'column',
                'x_title' : 'Weekday',
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ]
        )

add_worksheet(
        workbook,
        '24h',
        format_dict,
        field_dict,
        hour_dict,
        chart_list = [
            {
                'title' : '24h Consumption',
                'type' : 'column',
                'sub_type' : 'stacked',
                'x_title' : 'Hour',
                'y_title' : 'kWh',
                'series' : consumption_series,
                },
            {
                'title' : '24h Import',
                'type' : 'column',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : '24h Cost',
                'type' : 'column',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : 'Euro',
                'series' : full_cost_series,
                },
            {
                'title' : '24h Relative Cost',
                'type' : 'column',
                'x_title' : 'Hour',
                'y_title' : 'Euro',
                'series' : rel_cost_series,
                },
            ])

add_worksheet(
        workbook,
        'Tariff',
        format_dict,
        field_dict,
        tariff_dict,
        chart_list = [
            {
                'title' : 'Tariff Import',
                'type' : 'column',
                'x_title' : 'Tariff',
                'y_title' : 'kWh',
                'series' : import_series,
                },
            {
                'title' : 'Tariff Cost',
                'type' : 'column',
                'x_title' : 'Tariff',
                'y_title' : 'Euro',
                'series' : tariff_cost_series,
                },
            ]
        )

workbook.close()
