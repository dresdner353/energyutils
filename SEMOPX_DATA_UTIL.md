# SEMOpx Market Data Utility

SEMOpx provides day-ahead and intra-day electricity market trading for the Republic of Ireland and Northern Ireland as part of the Single Electricity Market (SEM).

Power auctions are run in several forms varying from day-ahead to three separate intra-day auctions. The data in relation to these auctions is made available via reports from the [semopx.com](https://semopx.com) website and also via their API.

This script implements the SEMOpx API and targets the retrtieval of both day-ahead (DA) and intra-day data (IDA1, IDA2, IDA3). When invoked, the script calls the API to first collect data on available reports for the specified ROI or NI market and then pulls that report data per given day. The data is converted from the SEMOpx format and written to JSONL files stored in a target directory. 

## Usage
```
usage: semopx_data_util.py [-h] [--odir ODIR] [--days DAYS] [--market {ROI,NI}] [--timezone TIMEZONE] [--verbose]

SEMOpx Data Retrieval Utility

options:
  -h, --help           show this help message and exit
  --odir ODIR          Output Directory for generated files
  --days DAYS          Backfill days (def 5)
  --market {ROI,NI}    Market Area (def ROI)
  --timezone TIMEZONE  Timezone def:Europe/Dublin
  --verbose            Enable verbose output
```

Options:
* --odir /path/to/output/directory  
This specifies the output directory for the retrieved data. Each day is written to a separate JSONL file.
* --days DAYS   
This is the number of days backlog to retrieve. The default is the last 5 days. SEMOpx only store data for about 1 year and as such this script could be run to pull back data for all available days by setting the --days option to a high number. 
* --market MARKET  
The market can be one of two values only.. ROI or NI. If a user wanted to track prices for both markets, you could separately invoke the script, each with a separate --odir and --market value
* --timezone TIMEZONE  
Allows for specifying of a timezone. The default is Europe/Dublin and should be fine for any processing within ROI/NI. 

## Operation
* The script is invoked with the selected market (--market), output directory (--odir) and number of days (--days) to retrieve
* When it calls the SEMOpx API, it does so in two stages:
   - The 1st stage paginates through a series of reports and collects a list of reports for the target number of days
   - The 2nd stage then retrieves each report, parsing the data and merging into a single file of records for each given day
* Retrieval acts incrementally, only pulling data for day files you do not already have or where the existing data was incomplete. 
* If you invoke the script with --days 100, it will retrieve data for the last 100 days
* If you immediately re-run the script, it will compute the last 100 reports but not retrieve any data after discovering that the files already exist in the --odir location. It may still retrieve the data for the day ahead because that data is incomplete (missing some or all of the intra-day data)
* This allows for incremental usage of the script on a daily basis or several times a day where it will only pull new data
* The data is written in JSONL files, one file per day, one line per 30-min interval.
* Prices are listed in Euro or GBP (based on the selected --market value of ROI or NI) and represent kWh values only. 
* SEMOpx actually provides data in mWh amounts in both Euro and GBP pricing but this script simplifies this to kWh and a single currency based on the target market.
* Time is presented in both EPOCH format (UTC seconds in 1970-01-01) and in local string format (YYYY/MM/DD HH:MM:SS) based on the selected timezone
* SEMOpx provides day-ahead data in hourly records and intra-day data in 30-min intervals. This script will always present a day as a set of 48 30-min records and double-up the DA data into 2 30-min records
* For daylight savings scenarios, some days will have 46 or 50 records based on the skipped or repeated hour
* Some of the intra-day prices will be missing from records either because the given auction was not performed or it did not apply to the given 30-min interval
* The script also calculates a final kwh rate based on a first available of IDA3, IDA2, IDA1 and DA rate. This order reflects the latest price for the given time period
* All rates in these files are ex-VAT
* For use in planning battery charging, the understanding is that you would use the "da_kwh_rate" value for this purpose. Based on current CRU doucments, the intention for the ROI is that suppliers set the dynamic market rate to the day-ahead (DA) values and not the IDA1-3 values.


## Example Call
```
python3 semopx_data_util.py --days 10 --market ROI --odir Desktop/semopx_data
Thu Jan  2 20:25:24 2025 Retrieving SEMOpx report details for days:10
Thu Jan  2 20:25:25 2025 Retrieving report page 1/0 (days:0)
Thu Jan  2 20:25:26 2025 Writing.. 1/10 Desktop/semopx_data/2025-01-03.jsonl
Thu Jan  2 20:25:28 2025 Writing.. 2/10 Desktop/semopx_data/2025-01-02.jsonl
Thu Jan  2 20:25:29 2025 Writing.. 3/10 Desktop/semopx_data/2025-01-01.jsonl
Thu Jan  2 20:25:31 2025 Writing.. 4/10 Desktop/semopx_data/2024-12-31.jsonl
Thu Jan  2 20:25:32 2025 Writing.. 5/10 Desktop/semopx_data/2024-12-30.jsonl
Thu Jan  2 20:25:34 2025 Writing.. 6/10 Desktop/semopx_data/2024-12-29.jsonl
Thu Jan  2 20:25:35 2025 Writing.. 7/10 Desktop/semopx_data/2024-12-28.jsonl
Thu Jan  2 20:25:37 2025 Writing.. 8/10 Desktop/semopx_data/2024-12-27.jsonl
Thu Jan  2 20:25:38 2025 Writing.. 9/10 Desktop/semopx_data/2024-12-26.jsonl
Thu Jan  2 20:25:40 2025 Writing.. 10/10 Desktop/semopx_data/2024-12-25.jsonl
Thu Jan  2 20:25:40 2025 Done.. retrieved 38/10 reports, skipped 0
```

## Sample File
```json
{"ts": 1734217200, "datetime": "2024/12/14 23:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1810, "da_kwh_rate": 0.1114, "final_kwh_rate": 0.1810}
{"ts": 1734219000, "datetime": "2024/12/14 23:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1744, "da_kwh_rate": 0.1114, "final_kwh_rate": 0.1744}
{"ts": 1734220800, "datetime": "2024/12/15 00:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1170, "da_kwh_rate": 0.0925, "final_kwh_rate": 0.1170}
{"ts": 1734222600, "datetime": "2024/12/15 00:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0910, "da_kwh_rate": 0.0925, "final_kwh_rate": 0.0910}
{"ts": 1734224400, "datetime": "2024/12/15 01:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0854, "da_kwh_rate": 0.0798, "final_kwh_rate": 0.0854}
{"ts": 1734226200, "datetime": "2024/12/15 01:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0550, "da_kwh_rate": 0.0798, "final_kwh_rate": 0.0550}
{"ts": 1734228000, "datetime": "2024/12/15 02:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0854, "da_kwh_rate": 0.0720, "final_kwh_rate": 0.0854}
{"ts": 1734229800, "datetime": "2024/12/15 02:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0603, "da_kwh_rate": 0.0720, "final_kwh_rate": 0.0603}
{"ts": 1734231600, "datetime": "2024/12/15 03:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0653, "da_kwh_rate": 0.0526, "final_kwh_rate": 0.0653}
{"ts": 1734233400, "datetime": "2024/12/15 03:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0503, "da_kwh_rate": 0.0526, "final_kwh_rate": 0.0503}
{"ts": 1734235200, "datetime": "2024/12/15 04:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0510, "da_kwh_rate": 0.0473, "final_kwh_rate": 0.0510}
{"ts": 1734237000, "datetime": "2024/12/15 04:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0392, "da_kwh_rate": 0.0473, "final_kwh_rate": 0.0392}
{"ts": 1734238800, "datetime": "2024/12/15 05:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0490, "da_kwh_rate": 0.0410, "final_kwh_rate": 0.0490}
{"ts": 1734240600, "datetime": "2024/12/15 05:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0430, "da_kwh_rate": 0.0410, "final_kwh_rate": 0.0430}
{"ts": 1734242400, "datetime": "2024/12/15 06:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0440, "da_kwh_rate": 0.0502, "final_kwh_rate": 0.0440}
{"ts": 1734244200, "datetime": "2024/12/15 06:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0650, "da_kwh_rate": 0.0502, "final_kwh_rate": 0.0650}
{"ts": 1734246000, "datetime": "2024/12/15 07:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0560, "da_kwh_rate": 0.0709, "final_kwh_rate": 0.0560}
{"ts": 1734247800, "datetime": "2024/12/15 07:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0780, "da_kwh_rate": 0.0709, "final_kwh_rate": 0.0780}
{"ts": 1734249600, "datetime": "2024/12/15 08:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0675, "da_kwh_rate": 0.0810, "final_kwh_rate": 0.0675}
{"ts": 1734251400, "datetime": "2024/12/15 08:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0810, "da_kwh_rate": 0.0810, "final_kwh_rate": 0.0810}
{"ts": 1734253200, "datetime": "2024/12/15 09:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0746, "da_kwh_rate": 0.0978, "final_kwh_rate": 0.0746}
{"ts": 1734255000, "datetime": "2024/12/15 09:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0820, "da_kwh_rate": 0.0978, "final_kwh_rate": 0.0820}
{"ts": 1734256800, "datetime": "2024/12/15 10:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0910, "da_kwh_rate": 0.1014, "final_kwh_rate": 0.0910}
{"ts": 1734258600, "datetime": "2024/12/15 10:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0910, "da_kwh_rate": 0.1014, "final_kwh_rate": 0.0910}
{"ts": 1734260400, "datetime": "2024/12/15 11:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0970, "da_kwh_rate": 0.0980, "ida2_kwh_rate": 0.0850, "final_kwh_rate": 0.0850}
{"ts": 1734262200, "datetime": "2024/12/15 11:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0980, "ida2_kwh_rate": 0.0850, "da_kwh_rate": 0.0980, "final_kwh_rate": 0.0850}
{"ts": 1734264000, "datetime": "2024/12/15 12:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0903, "da_kwh_rate": 0.1027, "ida2_kwh_rate": 0.0762, "final_kwh_rate": 0.0762}
{"ts": 1734265800, "datetime": "2024/12/15 12:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0903, "ida2_kwh_rate": 0.0762, "da_kwh_rate": 0.1027, "final_kwh_rate": 0.0762}
{"ts": 1734267600, "datetime": "2024/12/15 13:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0851, "da_kwh_rate": 0.0961, "ida2_kwh_rate": 0.0810, "final_kwh_rate": 0.0810}
{"ts": 1734269400, "datetime": "2024/12/15 13:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0810, "ida2_kwh_rate": 0.0760, "da_kwh_rate": 0.0961, "final_kwh_rate": 0.0760}
{"ts": 1734271200, "datetime": "2024/12/15 14:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0710, "da_kwh_rate": 0.0910, "ida2_kwh_rate": 0.0700, "final_kwh_rate": 0.0700}
{"ts": 1734273000, "datetime": "2024/12/15 14:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0630, "ida2_kwh_rate": 0.0650, "da_kwh_rate": 0.0910, "final_kwh_rate": 0.0650}
{"ts": 1734274800, "datetime": "2024/12/15 15:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0792, "da_kwh_rate": 0.0930, "ida2_kwh_rate": 0.0737, "final_kwh_rate": 0.0737}
{"ts": 1734276600, "datetime": "2024/12/15 15:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0930, "ida2_kwh_rate": 0.0877, "da_kwh_rate": 0.0930, "final_kwh_rate": 0.0877}
{"ts": 1734278400, "datetime": "2024/12/15 16:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1141, "da_kwh_rate": 0.1350, "ida2_kwh_rate": 0.1052, "final_kwh_rate": 0.1052}
{"ts": 1734280200, "datetime": "2024/12/15 16:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1220, "ida2_kwh_rate": 0.1150, "da_kwh_rate": 0.1350, "final_kwh_rate": 0.1150}
{"ts": 1734282000, "datetime": "2024/12/15 17:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1410, "ida3_kwh_rate": 0.1150, "da_kwh_rate": 0.1500, "ida2_kwh_rate": 0.1290, "final_kwh_rate": 0.1150}
{"ts": 1734283800, "datetime": "2024/12/15 17:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1390, "ida3_kwh_rate": 0.1150, "ida2_kwh_rate": 0.1290, "da_kwh_rate": 0.1500, "final_kwh_rate": 0.1150}
{"ts": 1734285600, "datetime": "2024/12/15 18:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1181, "ida3_kwh_rate": 0.1020, "da_kwh_rate": 0.1343, "ida2_kwh_rate": 0.1168, "final_kwh_rate": 0.1020}
{"ts": 1734287400, "datetime": "2024/12/15 18:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1106, "ida3_kwh_rate": 0.1090, "ida2_kwh_rate": 0.1110, "da_kwh_rate": 0.1343, "final_kwh_rate": 0.1090}
{"ts": 1734289200, "datetime": "2024/12/15 19:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1003, "ida3_kwh_rate": 0.1173, "da_kwh_rate": 0.1220, "ida2_kwh_rate": 0.1050, "final_kwh_rate": 0.1173}
{"ts": 1734291000, "datetime": "2024/12/15 19:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1003, "ida3_kwh_rate": 0.1194, "ida2_kwh_rate": 0.1100, "da_kwh_rate": 0.1220, "final_kwh_rate": 0.1194}
{"ts": 1734292800, "datetime": "2024/12/15 20:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1055, "ida3_kwh_rate": 0.0968, "da_kwh_rate": 0.0980, "ida2_kwh_rate": 0.1030, "final_kwh_rate": 0.0968}
{"ts": 1734294600, "datetime": "2024/12/15 20:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0750, "ida3_kwh_rate": 0.0750, "ida2_kwh_rate": 0.0910, "da_kwh_rate": 0.0980, "final_kwh_rate": 0.0750}
{"ts": 1734296400, "datetime": "2024/12/15 21:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0899, "ida3_kwh_rate": 0.0766, "da_kwh_rate": 0.0778, "ida2_kwh_rate": 0.0880, "final_kwh_rate": 0.0766}
{"ts": 1734298200, "datetime": "2024/12/15 21:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0644, "ida3_kwh_rate": 0.0651, "ida2_kwh_rate": 0.0710, "da_kwh_rate": 0.0778, "final_kwh_rate": 0.0651}
{"ts": 1734300000, "datetime": "2024/12/15 22:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0638, "ida3_kwh_rate": 0.0713, "da_kwh_rate": 0.0422, "ida2_kwh_rate": 0.0650, "final_kwh_rate": 0.0713}
{"ts": 1734301800, "datetime": "2024/12/15 22:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0204, "ida3_kwh_rate": 0.0359, "ida2_kwh_rate": 0.0292, "da_kwh_rate": 0.0422, "final_kwh_rate": 0.0359}
```

## Daylight Savings Scenarios
SEMOpx times are strictly in UTC format when published. To allow for both a UTC and local time mindset, each record contains a "ts" field and "datetime" field. The "ts" field is a epoch value and the "datetime" represents the converted local time. 

Under normal circumstances, each JSONL file will contain 48 lines, one line per half-hour, starting 23:00 on the night before to 22:00 on the following night. However in DST change days, the number of lines will vary to just 46 in spring when the clocks jump forward, skipping an hour and 50 lines in winter when the clock rolls back and repeats an hour.

The following examples highlight this behaviour:

### March 31st 2024 (day is 23 hours long, 1AM skipped)
```json
{"ts": 1711839600, "datetime": "2024/03/30 23:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0790, "da_kwh_rate": 0.0946, "final_kwh_rate": 0.0790}
{"ts": 1711841400, "datetime": "2024/03/30 23:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0850, "da_kwh_rate": 0.0946, "final_kwh_rate": 0.0850}
{"ts": 1711843200, "datetime": "2024/03/31 00:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0885, "da_kwh_rate": 0.0945, "final_kwh_rate": 0.0885}
{"ts": 1711845000, "datetime": "2024/03/31 00:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0952, "da_kwh_rate": 0.0945, "final_kwh_rate": 0.0952}
{"ts": 1711846800, "datetime": "2024/03/31 02:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0933, "da_kwh_rate": 0.0828, "final_kwh_rate": 0.0933}
{"ts": 1711848600, "datetime": "2024/03/31 02:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0809, "da_kwh_rate": 0.0828, "final_kwh_rate": 0.0809}
{"ts": 1711850400, "datetime": "2024/03/31 03:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0861, "da_kwh_rate": 0.0820, "final_kwh_rate": 0.0861}
{"ts": 1711852200, "datetime": "2024/03/31 03:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0790, "da_kwh_rate": 0.0820, "final_kwh_rate": 0.0790}
{"ts": 1711854000, "datetime": "2024/03/31 04:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0783, "da_kwh_rate": 0.0790, "final_kwh_rate": 0.0783}
{"ts": 1711855800, "datetime": "2024/03/31 04:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0680, "da_kwh_rate": 0.0790, "final_kwh_rate": 0.0680}
{"ts": 1711857600, "datetime": "2024/03/31 05:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0722, "da_kwh_rate": 0.0702, "final_kwh_rate": 0.0722}
{"ts": 1711859400, "datetime": "2024/03/31 05:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0708, "da_kwh_rate": 0.0702, "final_kwh_rate": 0.0708}
{"ts": 1711861200, "datetime": "2024/03/31 06:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0741, "da_kwh_rate": 0.0711, "final_kwh_rate": 0.0741}
{"ts": 1711863000, "datetime": "2024/03/31 06:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0701, "da_kwh_rate": 0.0711, "final_kwh_rate": 0.0701}
{"ts": 1711864800, "datetime": "2024/03/31 07:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0634, "da_kwh_rate": 0.0739, "final_kwh_rate": 0.0634}
{"ts": 1711866600, "datetime": "2024/03/31 07:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0690, "da_kwh_rate": 0.0739, "final_kwh_rate": 0.0690}
{"ts": 1711868400, "datetime": "2024/03/31 08:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0680, "da_kwh_rate": 0.0781, "final_kwh_rate": 0.0680}
{"ts": 1711870200, "datetime": "2024/03/31 08:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0753, "da_kwh_rate": 0.0781, "final_kwh_rate": 0.0753}
{"ts": 1711872000, "datetime": "2024/03/31 09:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0753, "da_kwh_rate": 0.0824, "final_kwh_rate": 0.0753}
{"ts": 1711873800, "datetime": "2024/03/31 09:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0750, "da_kwh_rate": 0.0824, "final_kwh_rate": 0.0750}
{"ts": 1711875600, "datetime": "2024/03/31 10:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0696, "da_kwh_rate": 0.0788, "final_kwh_rate": 0.0696}
{"ts": 1711877400, "datetime": "2024/03/31 10:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0675, "da_kwh_rate": 0.0788, "final_kwh_rate": 0.0675}
{"ts": 1711879200, "datetime": "2024/03/31 11:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0639, "da_kwh_rate": 0.0732, "ida2_kwh_rate": 0.0538, "final_kwh_rate": 0.0538}
{"ts": 1711881000, "datetime": "2024/03/31 11:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0606, "ida2_kwh_rate": 0.0514, "da_kwh_rate": 0.0732, "final_kwh_rate": 0.0514}
{"ts": 1711882800, "datetime": "2024/03/31 12:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0609, "da_kwh_rate": 0.0690, "ida2_kwh_rate": 0.0583, "final_kwh_rate": 0.0583}
{"ts": 1711884600, "datetime": "2024/03/31 12:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0591, "ida2_kwh_rate": 0.0586, "da_kwh_rate": 0.0690, "final_kwh_rate": 0.0586}
{"ts": 1711886400, "datetime": "2024/03/31 13:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0566, "da_kwh_rate": 0.0652, "ida2_kwh_rate": 0.0538, "final_kwh_rate": 0.0538}
{"ts": 1711888200, "datetime": "2024/03/31 13:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0541, "ida2_kwh_rate": 0.0538, "da_kwh_rate": 0.0652, "final_kwh_rate": 0.0538}
{"ts": 1711890000, "datetime": "2024/03/31 14:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0558, "da_kwh_rate": 0.0652, "ida2_kwh_rate": 0.0510, "final_kwh_rate": 0.0510}
{"ts": 1711891800, "datetime": "2024/03/31 14:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0527, "ida2_kwh_rate": 0.0490, "da_kwh_rate": 0.0652, "final_kwh_rate": 0.0490}
{"ts": 1711893600, "datetime": "2024/03/31 15:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0500, "da_kwh_rate": 0.0669, "ida2_kwh_rate": 0.0510, "final_kwh_rate": 0.0510}
{"ts": 1711895400, "datetime": "2024/03/31 15:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0574, "ida2_kwh_rate": 0.0560, "da_kwh_rate": 0.0669, "final_kwh_rate": 0.0560}
{"ts": 1711897200, "datetime": "2024/03/31 16:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0617, "da_kwh_rate": 0.0725, "ida2_kwh_rate": 0.0526, "final_kwh_rate": 0.0526}
{"ts": 1711899000, "datetime": "2024/03/31 16:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0663, "ida2_kwh_rate": 0.0574, "da_kwh_rate": 0.0725, "final_kwh_rate": 0.0574}
{"ts": 1711900800, "datetime": "2024/03/31 17:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0809, "ida3_kwh_rate": 0.0650, "da_kwh_rate": 0.0934, "ida2_kwh_rate": 0.0718, "final_kwh_rate": 0.0650}
{"ts": 1711902600, "datetime": "2024/03/31 17:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0933, "ida3_kwh_rate": 0.0930, "ida2_kwh_rate": 0.0819, "da_kwh_rate": 0.0934, "final_kwh_rate": 0.0930}
{"ts": 1711904400, "datetime": "2024/03/31 18:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1012, "ida3_kwh_rate": 0.0880, "da_kwh_rate": 0.1113, "ida2_kwh_rate": 0.0901, "final_kwh_rate": 0.0880}
{"ts": 1711906200, "datetime": "2024/03/31 18:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1051, "ida3_kwh_rate": 0.1001, "ida2_kwh_rate": 0.0947, "da_kwh_rate": 0.1113, "final_kwh_rate": 0.1001}
{"ts": 1711908000, "datetime": "2024/03/31 19:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0922, "ida3_kwh_rate": 0.1050, "da_kwh_rate": 0.1250, "ida2_kwh_rate": 0.0846, "final_kwh_rate": 0.1050}
{"ts": 1711909800, "datetime": "2024/03/31 19:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0922, "ida3_kwh_rate": 0.0650, "ida2_kwh_rate": 0.0810, "da_kwh_rate": 0.1250, "final_kwh_rate": 0.0650}
{"ts": 1711911600, "datetime": "2024/03/31 20:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0960, "ida3_kwh_rate": 0.0550, "da_kwh_rate": 0.1205, "ida2_kwh_rate": 0.0850, "final_kwh_rate": 0.0550}
{"ts": 1711913400, "datetime": "2024/03/31 20:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0809, "ida3_kwh_rate": 0.0550, "ida2_kwh_rate": 0.0739, "da_kwh_rate": 0.1205, "final_kwh_rate": 0.0550}
{"ts": 1711915200, "datetime": "2024/03/31 21:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0809, "ida3_kwh_rate": 0.0510, "da_kwh_rate": 0.1000, "ida2_kwh_rate": 0.0682, "final_kwh_rate": 0.0510}
{"ts": 1711917000, "datetime": "2024/03/31 21:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0637, "ida3_kwh_rate": 0.0510, "ida2_kwh_rate": 0.0510, "da_kwh_rate": 0.1000, "final_kwh_rate": 0.0510}
{"ts": 1711918800, "datetime": "2024/03/31 22:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0681, "ida3_kwh_rate": 0.0510, "da_kwh_rate": 0.0801, "ida2_kwh_rate": 0.0542, "final_kwh_rate": 0.0510}
{"ts": 1711920600, "datetime": "2024/03/31 22:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0580, "ida3_kwh_rate": 0.0510, "ida2_kwh_rate": 0.0510, "da_kwh_rate": 0.0801, "final_kwh_rate": 0.0510}
```

### October 27th 2024 (day is 25 hours long, two 1AM periods)
```json
{"ts": 1729980000, "datetime": "2024/10/26 23:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1762, "da_kwh_rate": 0.1711, "final_kwh_rate": 0.1762}
{"ts": 1729981800, "datetime": "2024/10/26 23:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1800, "da_kwh_rate": 0.1711, "final_kwh_rate": 0.1800}
{"ts": 1729983600, "datetime": "2024/10/27 00:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1800, "da_kwh_rate": 0.1802, "final_kwh_rate": 0.1800}
{"ts": 1729985400, "datetime": "2024/10/27 00:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1800, "da_kwh_rate": 0.1802, "final_kwh_rate": 0.1800}
{"ts": 1729987200, "datetime": "2024/10/27 01:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1650, "da_kwh_rate": 0.1962, "final_kwh_rate": 0.1650}
{"ts": 1729989000, "datetime": "2024/10/27 01:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1650, "da_kwh_rate": 0.1962, "final_kwh_rate": 0.1650}
{"ts": 1729990800, "datetime": "2024/10/27 01:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1630, "da_kwh_rate": 0.2030, "final_kwh_rate": 0.1630}
{"ts": 1729992600, "datetime": "2024/10/27 01:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1600, "da_kwh_rate": 0.2030, "final_kwh_rate": 0.1600}
{"ts": 1729994400, "datetime": "2024/10/27 02:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1630, "da_kwh_rate": 0.1636, "final_kwh_rate": 0.1630}
{"ts": 1729996200, "datetime": "2024/10/27 02:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1472, "da_kwh_rate": 0.1636, "final_kwh_rate": 0.1472}
{"ts": 1729998000, "datetime": "2024/10/27 03:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1250, "da_kwh_rate": 0.1379, "final_kwh_rate": 0.1250}
{"ts": 1729999800, "datetime": "2024/10/27 03:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1197, "da_kwh_rate": 0.1379, "final_kwh_rate": 0.1197}
{"ts": 1730001600, "datetime": "2024/10/27 04:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1284, "da_kwh_rate": 0.1154, "final_kwh_rate": 0.1284}
{"ts": 1730003400, "datetime": "2024/10/27 04:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1150, "da_kwh_rate": 0.1154, "final_kwh_rate": 0.1150}
{"ts": 1730005200, "datetime": "2024/10/27 05:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1107, "da_kwh_rate": 0.1220, "final_kwh_rate": 0.1107}
{"ts": 1730007000, "datetime": "2024/10/27 05:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1165, "da_kwh_rate": 0.1220, "final_kwh_rate": 0.1165}
{"ts": 1730008800, "datetime": "2024/10/27 06:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1115, "da_kwh_rate": 0.1484, "final_kwh_rate": 0.1115}
{"ts": 1730010600, "datetime": "2024/10/27 06:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1284, "da_kwh_rate": 0.1484, "final_kwh_rate": 0.1284}
{"ts": 1730012400, "datetime": "2024/10/27 07:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1125, "da_kwh_rate": 0.1065, "final_kwh_rate": 0.1125}
{"ts": 1730014200, "datetime": "2024/10/27 07:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1119, "da_kwh_rate": 0.1065, "final_kwh_rate": 0.1119}
{"ts": 1730016000, "datetime": "2024/10/27 08:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1084, "da_kwh_rate": 0.1101, "final_kwh_rate": 0.1084}
{"ts": 1730017800, "datetime": "2024/10/27 08:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1055, "da_kwh_rate": 0.1101, "final_kwh_rate": 0.1055}
{"ts": 1730019600, "datetime": "2024/10/27 09:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1150, "da_kwh_rate": 0.1020, "final_kwh_rate": 0.1150}
{"ts": 1730021400, "datetime": "2024/10/27 09:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1087, "da_kwh_rate": 0.1020, "final_kwh_rate": 0.1087}
{"ts": 1730023200, "datetime": "2024/10/27 10:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1134, "da_kwh_rate": 0.1009, "final_kwh_rate": 0.1134}
{"ts": 1730025000, "datetime": "2024/10/27 10:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1009, "da_kwh_rate": 0.1009, "final_kwh_rate": 0.1009}
{"ts": 1730026800, "datetime": "2024/10/27 11:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1040, "da_kwh_rate": 0.0950, "ida2_kwh_rate": 0.1120, "final_kwh_rate": 0.1120}
{"ts": 1730028600, "datetime": "2024/10/27 11:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0996, "ida2_kwh_rate": 0.0996, "da_kwh_rate": 0.0950, "final_kwh_rate": 0.0996}
{"ts": 1730030400, "datetime": "2024/10/27 12:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0966, "da_kwh_rate": 0.0935, "ida2_kwh_rate": 0.0950, "final_kwh_rate": 0.0950}
{"ts": 1730032200, "datetime": "2024/10/27 12:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0885, "ida2_kwh_rate": 0.0914, "da_kwh_rate": 0.0935, "final_kwh_rate": 0.0914}
{"ts": 1730034000, "datetime": "2024/10/27 13:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0902, "da_kwh_rate": 0.1003, "ida2_kwh_rate": 0.0910, "final_kwh_rate": 0.0910}
{"ts": 1730035800, "datetime": "2024/10/27 13:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0820, "ida2_kwh_rate": 0.0796, "da_kwh_rate": 0.1003, "final_kwh_rate": 0.0796}
{"ts": 1730037600, "datetime": "2024/10/27 14:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0879, "da_kwh_rate": 0.0960, "ida2_kwh_rate": 0.1008, "final_kwh_rate": 0.1008}
{"ts": 1730039400, "datetime": "2024/10/27 14:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0899, "ida2_kwh_rate": 0.1066, "da_kwh_rate": 0.0960, "final_kwh_rate": 0.1066}
{"ts": 1730041200, "datetime": "2024/10/27 15:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0801, "da_kwh_rate": 0.1020, "ida2_kwh_rate": 0.1053, "final_kwh_rate": 0.1053}
{"ts": 1730043000, "datetime": "2024/10/27 15:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.0949, "ida2_kwh_rate": 0.1130, "da_kwh_rate": 0.1020, "final_kwh_rate": 0.1130}
{"ts": 1730044800, "datetime": "2024/10/27 16:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1053, "da_kwh_rate": 0.1280, "ida2_kwh_rate": 0.1230, "final_kwh_rate": 0.1230}
{"ts": 1730046600, "datetime": "2024/10/27 16:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1274, "ida2_kwh_rate": 0.1450, "da_kwh_rate": 0.1280, "final_kwh_rate": 0.1450}
{"ts": 1730048400, "datetime": "2024/10/27 17:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1350, "ida3_kwh_rate": 0.1460, "da_kwh_rate": 0.1404, "ida2_kwh_rate": 0.1404, "final_kwh_rate": 0.1460}
{"ts": 1730050200, "datetime": "2024/10/27 17:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1313, "ida3_kwh_rate": 0.1621, "ida2_kwh_rate": 0.1404, "da_kwh_rate": 0.1404, "final_kwh_rate": 0.1621}
{"ts": 1730052000, "datetime": "2024/10/27 18:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1384, "ida3_kwh_rate": 0.1665, "da_kwh_rate": 0.1206, "ida2_kwh_rate": 0.1404, "final_kwh_rate": 0.1665}
{"ts": 1730053800, "datetime": "2024/10/27 18:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1274, "ida3_kwh_rate": 0.1324, "ida2_kwh_rate": 0.1379, "da_kwh_rate": 0.1206, "final_kwh_rate": 0.1324}
{"ts": 1730055600, "datetime": "2024/10/27 19:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1303, "ida3_kwh_rate": 0.1317, "da_kwh_rate": 0.1100, "ida2_kwh_rate": 0.1404, "final_kwh_rate": 0.1317}
{"ts": 1730057400, "datetime": "2024/10/27 19:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1217, "ida3_kwh_rate": 0.1304, "ida2_kwh_rate": 0.1372, "da_kwh_rate": 0.1100, "final_kwh_rate": 0.1304}
{"ts": 1730059200, "datetime": "2024/10/27 20:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1200, "ida3_kwh_rate": 0.1600, "da_kwh_rate": 0.1013, "ida2_kwh_rate": 0.1354, "final_kwh_rate": 0.1600}
{"ts": 1730061000, "datetime": "2024/10/27 20:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1191, "ida3_kwh_rate": 0.1665, "ida2_kwh_rate": 0.1313, "da_kwh_rate": 0.1013, "final_kwh_rate": 0.1665}
{"ts": 1730062800, "datetime": "2024/10/27 21:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1244, "ida3_kwh_rate": 0.1860, "da_kwh_rate": 0.0920, "ida2_kwh_rate": 0.1542, "final_kwh_rate": 0.1860}
{"ts": 1730064600, "datetime": "2024/10/27 21:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1121, "ida3_kwh_rate": 0.1297, "ida2_kwh_rate": 0.1263, "da_kwh_rate": 0.0920, "final_kwh_rate": 0.1297}
{"ts": 1730066400, "datetime": "2024/10/27 22:00:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1119, "ida3_kwh_rate": 0.1350, "da_kwh_rate": 0.0801, "ida2_kwh_rate": 0.1260, "final_kwh_rate": 0.1350}
{"ts": 1730068200, "datetime": "2024/10/27 22:30:00", "market_area": "ROI", "currency": "euro", "ida1_kwh_rate": 0.1100, "ida3_kwh_rate": 0.1120, "ida2_kwh_rate": 0.1140, "da_kwh_rate": 0.0801, "final_kwh_rate": 0.1120}
```
