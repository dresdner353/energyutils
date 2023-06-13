# Battery Simulator

This script takes a directory of JSONL files derived from the esb_hdf_reader.py or shelly_em_data_util.py scripts and performs a battery simulation. 

This is essentually a data scrub, reducing per-hour export and import accordingly as if the simulated battery had been present to divert surplus export to battery and later reduce import by discharging the battery. The resulting data is then output to another directory. 

Cost reports may then be generated from the scrubbed data set to provide accurate estimates on additional savings by using a battery. This could also be used to simulate more battery storage on a setup thaty already uses a battery.

## Usage
```
usage: battery_sim.py [-h] --idir IDIR --odir ODIR [--start START] [--end END]
                      [--timezone TIMEZONE] --battery_capacity BATTERY_CAPACITY 
                      --max_charge_percent 1-100 
                      --min_discharge_percent 1-100
                      --charge_rate CHARGE_RATE 
                      --discharge_rate DISCHARGE_RATE
                      [--discharge_bypass_interval DISCHARGE_BYPASS_INTERVAL]
                      [--export_charge_boundary EXPORT_CHARGE_BOUNDARY]
                      [--decimal_places DECIMAL_PLACES] 
                      [--verbose]

Battery Simulator

optional arguments:
  -h, --help            show this help message and exit
  --idir IDIR           Input Directory for data files
  --odir ODIR           Output Directory for modifled data files
  --start START         Calculation Start Date (YYYYMMDD)
  --end END             Calculation End Date (YYYYMMDD)
  --timezone TIMEZONE   Timezone
  --battery_capacity BATTERY_CAPACITY
                        Battery Capacity (kWh)
  --max_charge_percent 
                        Battery Max Charge Percentage (1..100)
  --min_discharge_percent 
                        Battery Min Discharge Percentage (1..100)
  --charge_rate CHARGE_RATE
                        Battery Charge Rate (kWh/hour)
  --discharge_rate DISCHARGE_RATE
                        Battery Discharge Rate (kWh/hour)
  --discharge_bypass_interval DISCHARGE_BYPASS_INTERVAL
                        Time Interval for Discharge Bypass <HH-HH>
  --export_charge_boundary EXPORT_CHARGE_BOUNDARY
                        Min Export required for charging (kWh/hour)
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:4)
  --verbose             Enable verbose output
```

## Notes
* There is no DC-DC loss factor considered here for now. So a kWh stolen from export is assumed to get into the simulated battery as a kwH. In reality there will need to be a loss factor added here. 
* For each hour: 
  - The first step performed is to steal export if export exists and the simulated battery has capacity to take on more charge. 
  - Then the import for the same hour is checked and offset from the battery storage. 
  - So this gives a best possible outcome in favour of the battery per hour by acting as if all the export happened before all the import took place. 
* The hour to hour simulation will inherit any existing charge from the previous hour. 
  - Therefore as the daytime passes and export drops to 0, the remaining battery charge will continue to be drawn down to offset any import that took place. 
  - This will continue until the battery reaches the min charge or we roll into the next day and export starts to occur again charing the battery


## Example Run
```
python3 battery_sim.py \
            --idir /path/to/original/esb_data \
            --odir /tmp  \
            --battery_capacity 10 \
            --max_charge_percent 95 \
            --min_discharge_percent 5 \
            --charge_rate 2 \
            --discharge_rate 2 \
            --discharge_bypass_interval 02-05

Tue Jun 13 18:33:21 2023 Loaded 75 files, 1776 records
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-26.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-27.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-28.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-29.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-30.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-01-31.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-02-01.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-02-02.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-02-03.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-02-04.jsonl
......
......
......
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-05.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-06.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-07.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-08.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-09.jsonl
Tue Jun 13 18:33:21 2023 Writing to /tmp/2023-04-10.jsonl
Tue Jun 13 18:33:21 2023 Final battery state.. charge:9.45kWh (94%) ovl_charge:84.08kWh (8 cycles) ovl_discharge:74.63kWh
```

Notes:
* Battery capacity set to 10 kWh, with a min and max charge capacity set to 5% and 95%
* The battery can charge at max 2kWh/hour and discharge as the same 2kWh/hour rate
* Discharge is disabled between 2-5AM (allows for EV rates where discharge may not be desired)
* After the sweep was complete, the simulated battery still had 9.45kWh (94%) left and had charged a total of 84.08kWh (8 full cycles) and discharged a total of 74.63kWh.
