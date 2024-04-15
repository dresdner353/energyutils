# Battery Simulator

This script takes a directory of JSONL files derived from the esb_hdf_reader.py or shelly_em_data_util.py scripts and performs a battery simulation. 

This is essentually a data scrub, reducing per-hour export and import accordingly as if the simulated battery had been present to divert surplus export to battery and later reduce import by discharging the battery. The resulting data is then output to another directory. 

Cost reports may then be generated from the scrubbed data set to provide accurate estimates on additional savings by using a battery. This could also be used to simulate more battery storage on a setup thaty already uses a battery.

## Usage
```

usage: battery_sim.py [-h] --idir IDIR --odir ODIR [--start START] [--end END]
                      [--timezone TIMEZONE] --battery_capacity
                      BATTERY_CAPACITY --max_charge_percent
                      --min_charge_percent
                      --charge_rate CHARGE_RATE --discharge_rate
                      DISCHARGE_RATE
                      [--charge_loss_percent]
                      [--discharge_loss_percent]
                      [--discharge_bypass_interval DISCHARGE_BYPASS_INTERVAL]
                      [--grid_shift_interval GRID_SHIFT_INTERVAL]
                      [--fit_discharge_interval FIT_DISCHARGE_INTERVAL]
                      [--export_charge_boundary EXPORT_CHARGE_BOUNDARY]
                      [--decimal_places DECIMAL_PLACES] [--verbose]

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
  --max_charge_percent 1-100
                        Battery Max Charge Percentage (1..100)
  --min_charge_percent 1-100
                        Battery Min Charge Percentage (1..100)
  --charge_rate CHARGE_RATE
                        Battery Charge Rate (kWh/hour)
  --discharge_rate DISCHARGE_RATE
                        Battery Discharge Rate (kWh/hour)
  --charge_loss_percent 0-100
                        Charge Loss Percentage (1..100) def:7
  --discharge_loss_percent 0-100
                        Discharge Loss Percentage (1..100) def:7
  --discharge_bypass_interval DISCHARGE_BYPASS_INTERVAL
                        Time Interval for Discharge Bypass <HH-HH>
  --grid_shift_interval GRID_SHIFT_INTERVAL
                        Time Interval for Grid Charging <HH-HH>
  --fit_discharge_interval FIT_DISCHARGE_INTERVAL
                        Time Interval for FIT discharge <HH-HH>
  --export_charge_boundary EXPORT_CHARGE_BOUNDARY
                        Min Export required for charging (kWh/hour)
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:4)
  --verbose             Enable verbose output



```

## Options
* --idir /path/to/input/files  
This is a path to a directory containing the JSONL files output from the esb_hdf_reader.py script. These files serve as the input data set to use in performing the battery simulation.
* --odir /path/to/output/files  
This is where the battery simulation results we will written. It is essentially a new set of JSONL files generated from the original files. The import and export values of the original data set will be modified to reflect the battery simulation.
* --start YYYYMMDD and --end YYYYMMDD  
The --start YYYYMMDD and --end YYYYMMDD options may be used to limit the simualation to a specified time period. For example --start 20230901 --end 20240203 will only include data from September 1st 2023 to Feb 3rd 2024. If both fields are omitted, then the simulation works on all data available in the input data set. You can also opt to use one or the other on their own to limit only the start or end dates.
* --timezone <named time zone>  
This option allows the assertion of a specific timezone. The default value is "Europe/Dublin". In most cases this need not be touched for any kind of processing for Ireland or the UK. The values used should confirm to the tzdata definition found in https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. For example, to run this for Austria, you would use --timezone "Europe/Vienna". Those named definitions are represented in the universal tzdata database which knows all about local UTC offsets and daylight saving adjustments that apply to the given location. This then ensures the correct time adjustments and calculations.
* --battery_capacity <size>  
This is the simulated battery capacity in kWh. So --battery 20 would set the max battery 100% storage to be 20kWh in total. 
* --max_charge_percent 1-100 . 
This is the max percent charge that the battery is allowed to reach. This is nearly always 100. If a battery specification indicated max charge or 75% or for simulation purposes, you wished to limit the max charge to 75%, then you use specify --max_charge_percent 75. The percentage symbol is not used in value. 
* --min_charge_percent 1-100 . 
This is minimum charge perentages and represents a number between 1 and 100 to indicate the minimum charge percentage. Most batteries do not allow discharge to zero, therefore it is quite typical to have this value set to 10 or even 20 depending on the specific battery being used.
* --charge_rate CHARGE_RATE  
This is the rate of charge in kWh units per hour. A value of --charge_rate 2.5 would define a charging rate of 2.5kWh per hour.  
* --discharge_rate DISCHARGE_RATE . 
This defines the discharge rate in kWh. A value of 1.5 would define a discharge rate of 1.5kWh per hour
* --charge_loss_percent 0-100 . 
This defines a loss percentage applied to the battery charging. The value is in percent. So if --charge_loss_percent 7 was used, it would mean that 7% of AC used for the charge would be lost. For example 3kWh of AC diverted to the battery would result in 2.79 charge getting into the battery. The lost 0.21kWh represents 7% of the lost charge.
* --discharge_loss_percent 0-100 . 
This defines a loss percentage applied to the battery discharging. The value is in percent. So if --discharge_loss_percent 7 was used, it would mean that 7% of battery discharge would be lost. For example 3kWh discharged from the battery would result in 2.79 AC. The lost 0.21 represents 7% of the lost charge.
* --grid_shift_interval HH-HH .  
This is the optional daily grid shift interval. To set the simulated grid shift to run from 2-6 AM each day, then use --grid_shift_interval 02-06. 
* --discharge_bypass_interval HH-HH  
This specifies a daily interval where discharge is prevented. Ideally, this can be set to the same time as a grid shift interval but is managed separately to allow for protection of battery charge if the night period is longer than the EV charging period. 
* --fit_discharge_interval HH-HH  
This sets another interval for forced FIT discharge where a user wishes to export existing battery charge to earn FIT, usually prior to the grid shift period. The same format applies using the start and end hours separated by a dash. So --fit_discharge_interval 17-19 will try to discharge the battery between 5pm and 7pm daily.
* --export_charge_boundary EXPORT_CHARGE_BOUNDARY . 
This defines a minimum export level per hour to justify any form of battery charging. The default value is 0.05 (50Wh) and should be ideal for most simulations.
* --decimal_places DECIMAL_PLACES  
Sets the decimal places in the results. The default value here is 4 and should be perfect for nearly all use cases
* --verbose             Enable verbose output



## The Simulation Process
* For each hour: 
  - The first step performed is to steal availble export if the simulated battery has capacity to take a charge. 
  - Then the import for the same hour is checked and offset from existing battery storage. 
  - So this gives a best possible outcome in favour of the battery on a per hour basis by acting as if all the export happened before all the import took place. 
* The hour to hour simulation will inherit any existing charge from the previous hour. 
  - Therefore as the daytime passes and export drops to 0, the remaining battery charge will continue to be drawn down to offset any import that took place. 
  - This will continue until the battery reaches the min charge or we roll into the next day and export starts to occur again charging the battery
* As each hourly record is processed the following fields are changed:
  - export is reduced by any amount charged to the battery
  - import is reduced by any amount discharged from the battery
* If grid shift or FIT discharge intervals are set, then addiional charging and discharging will take place in the designated times
* The following fields are added to the new data set:
  - battery_charge.. the kWh charge added in that hour 
  - battery_discharge.. the kWh discharge used in that hour 
  - battery_storage.. the remaining kWh stored in the battery
  - battery_capacity.. the battery capacity (percentage) remaining
* Those additional fields are then used in the gen_report.py script to produce additional charts in relation to battery charge
* The reduced export and import fields will also impact costing in the new report and serve as a way to determine the savings effect of the battery simulation


## Example Run
```
python3 battery_sim.py \
            --idir /path/to/original/esb_data \
            --odir /tmp  \
            --battery_capacity 10 \
            --max_charge_percent 95 \
            --min_charge_percent 5 \
            --charge_rate 2 \
            --discharge_rate 2 \
            --discharge_bypass_interval 02-08 \
            --grid_shift_interval 02-04

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
* The battery can charge at max 2kWh/hour and discharge at the same 2kWh/hour rate
* Discharge is disabled between 2-8AM 
* Grid shift is set to charge the battery between hours 2-4AM
