import argparse
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo
import sys
import xlsxwriter

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
            'width' : 10,
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
            'format' : 'currency_4dp',
            },

        'da_kwh_rate' : {
            'title' : 'DA Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'currency_4dp',
            },
        'ida1_kwh_rate' : {
            'title' : 'IDA1 Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'currency_4dp',
            },
        'ida2_kwh_rate' : {
            'title' : 'IDA2 Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'currency_4dp',
            },
        'ida3_kwh_rate' : {
            'title' : 'IDA3 Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'currency_4dp',
            },
        'final_kwh_rate' : {
            'title' : 'Final Rate',
            'width' : 12,
            'header_format' : 'header',
            'format' : 'currency_4dp',
            },
        }

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
        first_field,
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
    # construction order and first field is then 
    # located to front
    header_fields = list(field_dict.keys())
    header_fields.remove(first_field)
    header_fields.insert(0, first_field)

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
    
        col_options = {}

        # column hiding
        # but bypass hiding of first field
        if (field != first_field and 
            'hidden' in field_rec):
            col_options['hidden'] = field_rec['hidden']

        # column width
        worksheet.set_column(
                field_rec['col'], 
                field_rec['col'], 
                field_rec['width'],
                options = col_options)

    # Freeze top row and 
    # set height to 2 rows
    worksheet.freeze_panes(1, 0)
    worksheet.set_row(0, 40)

    # data incremental sort on key
    key_list = list(data_dict.keys())
    key_list.sort()

    # Enable Auto Filter across all columns
    worksheet.autofilter(0, 0, 0, len(header_fields) - 1)  

    # Default auto-filtered state
    # certain first_field values 
    # will trigger a default auto-filter
    # to try and reduce the displayed value set
    #
    # datetime (hour sheet) will filter the last 1 day
    # day will filter the last 40 days
    # week will filter the last 1 year
    # etc
    filtered_field = None
    max_filter_periods = None
    default_filter_dict = {
            'datetime' : {
                'field' : 'month',
                'periods' : 1
                },
            }

    if first_field in default_filter_dict:
        # determine the name of the field to filter
        # and its related column
        filtered_field = default_filter_dict[first_field]['field']
        max_filter_periods = default_filter_dict[first_field]['periods']
        filtered_field_rec = field_dict[filtered_field]

        if 'hidden' in filtered_field_rec:
            # filter field is hidden, auto-filter disabled
            filtered_field = None
        else:
            filter_col = filtered_field_rec['col']

            # unique set of selected filter key values
            filter_field_set = set()
            for k in data_dict:
                filter_field_set.add(data_dict[k][filtered_field])

            # sort key list and reduce to last N items
            filter_key_list = list(filter_field_set)
            filter_key_list.sort()
            filter_key_list = filter_key_list[-max_filter_periods:]

            # populate the filter list with the 
            # selected list of values
            # Note: This sets up the filter 
            # but the rows are not hidden
            # see further on
            worksheet.filter_column_list(
                    filter_col,
                    filter_key_list)
    
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
            elif field_rec['format'] in [
                    'integer', 
                    'float', 
                    'currency_4dp', 
                    'currency_2dp', 
                    'percent', 
                    'vac',
                    'kwh',
                    'kwh_3dp']:
                if field in rec:
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

        # auto-hide row for filtered scenario
        # applies only if the given row's filter field value
        # is not in the filter value list
        if (filtered_field and 
            not rec[filtered_field] in filter_key_list):
            worksheet.set_row(row, options={"hidden": True})

    # Charts
    if not chart_list:
        return

    # charts positioned underneath data
    # vertically stacked
    chart_col = 0
    chart_row = row + 2

    for chart_rec in chart_list:
        chart_def = {
                    'type': chart_rec['type'],
                    }
        if 'sub_type' in chart_rec:
            chart_def['subtype'] = chart_rec['sub_type']
        chart = workbook.add_chart(chart_def)

        chart.set_title({'name': chart_rec['title']})
        chart.set_size({'width': 2048, 'height': 768})

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
            worksheet.insert_chart(
                    chart_row,
                    chart_col,
                    chart)

            # next chart 40 lines later
            # comfortable gap between charts
            chart_row += 40

    return


def load_data(
        idir,
        start_date,
        end_date,
        time_zone,
        tariff_list,
        interval_list,
        vat_rate):

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
    
    # VAT rate to factor
    vat_factor = 1 + (vat_rate / 100)

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
    
                # store keyed on ts field
                data_dict[rec['ts']] = rec

                # populate time keys from parsed ts
                dt_ref = datetime.datetime.fromtimestamp(
                        rec['ts'], 
                        tz = zoneinfo.ZoneInfo(time_zone))

                rec['hour'] = dt_ref.hour
                rec['day'] = '%04d-%02d-%02d' % (
                  dt_ref.year, 
                  dt_ref.month, 
                  dt_ref.day)
                rec['month'] = '%04d-%02d' % (
                  dt_ref.year, 
                  dt_ref.month) 
                rec['year'] = '%04d' %(
                  dt_ref.year)
                rec['weekday'] = dt_ref.strftime('%u %a')
                rec['week'] = dt_ref.strftime('%Y-%W')

                # tariff calculation based on week day number and hour
                dt_weekday = int(dt_ref.strftime('%u'))
                dt_hour = rec['hour']

                # Import Tariff and charging rates
                if (dt_weekday in tarff_interval_dict and 
                    dt_hour in tarff_interval_dict[dt_weekday]):
                    rec['tariff_name'] = tarff_interval_dict[dt_weekday][dt_hour]
                    rec['tariff_rate'] = tariff_dict[rec['tariff_name']]

                # VAT adjustment
                rate_field_list = [
                        'da_kwh_rate', 
                        'ida1_kwh_rate', 
                        'ida2_kwh_rate', 
                        'ida3_kwh_rate', 
                        'final_kwh_rate'
                        ]

                for rate_field in rate_field_list:
                    if rate_field in rec:
                        rec[rate_field] = rec[rate_field] * vat_factor

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
        description = 'SEMPpx Data Report Generator'
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
        '--currency', 
        help = 'Currency Sumbol (def:€)', 
        default = '€',
        required = False
        )

parser.add_argument(
        '--vat', 
        help = 'VAT Rate (def:0.. range 1-100)', 
        default = 0,
        type = float,
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
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

parser.add_argument(
        '--hide_columns', 
        help = 'columns to hide',
        nargs = '*',
        required = False,
        choices = list(field_dict.keys()),
        default = []
        )

args = vars(parser.parse_args())
report_file_name = args['file']
tariff_list = args['tariff_rate']
interval_list = args['tariff_interval']
vat_rate = args['vat']
idir = args['idir']
start_date = args['start']
end_date = args['end']
timezone = args['timezone']
currency_symbol = args['currency']
hide_column_list = args['hide_columns']
verbose = args['verbose']

# populate hidden boolean into field dict
for column_key in hide_column_list:
    if column_key in field_dict:
        field_dict[column_key]['hidden'] = True

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
        timezone,
        tariff_list,
        interval_list,
        vat_rate)

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
        'title': 'SEMOpx Rate Report',
        'subject': 'Python-generated Excel report based on SEMOpx auction data',
        'keywords': 'python energy report',
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

kwh_format = workbook.add_format() 
# with commas and 2 decimal places
kwh_format.set_num_format('#,##0.00 "kWh"') 
format_dict['kwh'] = kwh_format

# 3dp variant of kwh 
# only needed for smaller offset-type fields
kwh_3dp_format = workbook.add_format() 
# with commas and 3 decimal places
kwh_3dp_format.set_num_format('#,##0.000 "kWh"') 
format_dict['kwh_3dp'] = kwh_3dp_format

vac_format = workbook.add_format() 
# with commas and 2 decimal place
vac_format.set_num_format('#,##0.00 "V"') 
format_dict['vac'] = vac_format

percent_format = workbook.add_format() 
percent_format.set_num_format('0.0%') 
format_dict['percent'] = percent_format

currency_4dp_format = workbook.add_format() 
# with currency symbol, commas and 4 decimal places
currency_4dp_format.set_num_format(
        '%s#,##0.0000;[BLUE]-%s#,##0.0000' % (
            currency_symbol,
            currency_symbol
            )
        ) 
format_dict['currency_4dp'] = currency_4dp_format

currency_2dp_format = workbook.add_format() 
# with currency symbol, commas and 2 decimal places
currency_2dp_format.set_num_format(
        '%s#,##0.00;[BLUE]-%s#,##0.00' % (
            currency_symbol,
            currency_symbol
            )
        ) 
format_dict['currency_2dp'] = currency_2dp_format

# sheet

cost_label = 'Cost (%s)' % (currency_symbol)

da_series =  [
        {
            'field': 'tariff_rate',
            'colour': 'red',
            },
        {
            'field': 'da_kwh_rate',
            'colour': 'green',
            },
        ]

final_series =  [
        {
            'field': 'tariff_rate',
            'colour': 'red',
            },
        {
            'field': 'final_kwh_rate',
            'colour': 'blue',
            },
        ]

add_worksheet(
        workbook,
        '30-min',
        format_dict,
        field_dict,
        data_dict,
        'datetime',
        chart_list = [
            {
                'title' : 'DA Rate Vs Tariff Rate',
                'type' : 'line',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : cost_label,
                'series' : da_series,
            },
            {
                'title' : 'Final Rate Vs Tariff Rate',
                'type' : 'line',
                'x_title' : 'Hour',
                'x_rotation' : -45,
                'y_title' : cost_label,
                'series' : final_series,
            },
            ]
        )

workbook.close()
