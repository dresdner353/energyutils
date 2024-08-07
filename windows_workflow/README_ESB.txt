Steps to get your ESB report generating on Microsoft Windows:

* Download The energyutils codebase
----------------------------------------------------------------------------
- Browse to https://github.com/dresdner353/energyutils 
- From there, look for the green Code button, click it and select the download ZIP file 
- In Windows explorer, right-click and "extract all" files (as you might do with a zip file usually). 
  But do not double-click to open it as that will not work correctly. 
- Navigate to a folder called "windows_workflow" and open the README_ESB.txt file (it's actually this very file you are reading now)


* Install Python3
----------------------------------------------------------------------------
Launch the Microsoft Store and search for python3. 
Install by clicking the "Get" button

Note: You need python 3.9 or later. At the time of writing, the version Microsoft had 
listed was 3.11


* Run initial setup script
----------------------------------------------------------------------------
In the windows_workflow folder, double-click the batch script called "init_setup".

Note:You may be warned about this as being an unknown program and feel free to 
virus scan etc. But depending on your virus scanner etc, you may have to 
Click on a "Run anyway" to kick it off. Windows Defender will popup a dialog with 
button "Don't run", but to run it, you click on the "More info" link and there is a 
"Run anyway" option to launch it.

This script only runs Python3 and install required modules for 
the report scripts. 


* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, double-click on "gen_esb_report". This should parse out data from the 
sample file "HDF_EXAMPLE.csv" in the "hdf_files" sub-folder and then generate 
Excel report files in the windows_workflow folder. 

Note: You will likely get the same warnings before running this script as above


* Put your own ESB HDF file(s) in place
----------------------------------------------------------------------------
Download your latest ESB HDF file and drop it into the "hdf_files" sub-folder.

Note: Make sure that once you have your own file in place, that you should delete 
the "HDF_EXAMPLE.csv" file. If you leave that file there, its data will be merged with 
your own data and give inaccurate results.

Note: Going forward, you can download new HDF files from ESBN and drop these into this
"hdf_files" sub-folder. You have the option of leaving the old files there or deleting them.
The script reads all CSV files in this "hdf_files" sub-folder and combines the data, over-writing
duplicate days automatically. This can be useful if you switch provider as the ESBN wipe 
you older HDF data, only serving you up new data since the switch. So having the ability to 
process multiple files works around this. 


* Customise the Report pricing detail
----------------------------------------------------------------------------
This can be the tricky part. If you right-click on the gen_esb_report file and 
select edit, it should launch Windows Notepad and this lets you edit the script
itself.

As you glance down the file, there are four stacks of code similar to this example:

REM Example EV report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_ev.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 ^
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost ^
    --annual_standing_charge 396 ^
    --fit_rate 0.21 


That code invokes the report generator to generate an Excel file called esb_report_ev.xlsx
The line that starts with "--tariff_rate" defines three tariffs.. Day, Night and Boost. 
The values are defined after the tariff label. So Day:0.4320 defines the day kWh rate as 
0.4320 Euro. You can have as many of these on the line as required for your given 
electricity plan. 

The line starting with "--tariff_interval" defines day/hour ranges and the matching tariff. In
the above example, it says hours 08-23 are the Day tariff and hours 23-08 are the night and 02-04 
are the Boost tariff. You can also optionally prefix this with a day range 1-7 to depict tariffs
for specific days. There is an example at the bottom of that file showing a plan that uses a free tariff
between 9 and 5pm on Sundays.

Lastly, the --annual_standing_charge value is yearly standing charge. 

See:
https://github.com/dresdner353/energyutils/blob/main/GEN_REPORT.md
for full documentation on the options available for this tool.

The whole point of this is to allow you customise the pricing to match your desired plan. The cost calculations
then shown will closely match the actual costs you would be incurring. The only gap these calculations would 
have are things like PSO levies and other kinds of credits. But you could run several reports on your data
against pricing from multiple suppliers to compare the results you get from each one.
