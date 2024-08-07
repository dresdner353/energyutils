Steps to get your ESB report generating on Mac/Linux:

* Download The energyutils codebase
----------------------------------------------------------------------------
- Browse to https://github.com/dresdner353/energyutils 
- From there, look for the green Code button, click it and select the download ZIP file 
- In Finder double-click the downloaded zip file to extract its contents into a new folder. 
- Alternatively git clone https://github.com/dresdner353/energyutils.git
- Navigate to a folder called "xnix_workflow" and open the README.txt 
  file (it's actually this very file you are reading now)


* Install Python3 (MacOS)
----------------------------------------------------------------------------
The scripts require Python 3.9 or later. 

Recent versions of MacOS ship now with Python3 but it is an older version
than the required 3.9. So it is recommended to install Python3 via homebrew. 

For more information, follow instructions listed here to install python3 on MacOS.. 
https://docs.python-guide.org/starting/install3/osx/


* Install Python3 (Linux)
----------------------------------------------------------------------------
The scripts require Python 3.9 or later. 

Most Linux distros will have some version of Python3 now included. Check on your distro 
package management what version you have and try to get the latest Python3 version >= 3.9.  


* Required modules
----------------------------------------------------------------------------
The scripts require a few extra modules beyond the base install of Python. The recommended
approach is to install these modules using pip:

So either of these approaches should work:

pip3 install --user tzdata requests xlsxwriter python-dateutil cherrypy

or 

python3 -m pip install --user tzdata requests xlsxwriter python-dateutil cherrypy


* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, run "gen_esb_report.sh". 

This should parse out data from the sample file "HDF_EXAMPLE.csv" in the "hdf_files" 
sub-folder and then generate Excel report files in the windows_workflow folder. 


* Put the ESB HDF file in place
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
Edit the gen_esb_report.sh script to customise the pricing detail.

As you glance down the file, you will find this code:

python3 ${GEN_REPORT_SCRIPT} \
    --idir "${HDF_DATA}" \
    --file esb_report.xlsx \
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --annual_standing_charge 396 \
    --fit_rate 0.21 

That shell command invokes the report generator to generate an Excel file called esb_report.xlsx
The line that starts with "--tariff_rate" defines three tariffs.. Day, Night and Boost. 
The values are defined after the tariff label. So Day:0.4320 defines the day kWh rate as 
0.4320 Euro. You can have as many of these on the line as required for your given 
electricity plan. 

The line starting with "--tariff_interval" defines day/hour ranges and the matching tariff. In
the above example, it says hours 08-23 are the Day tariff and hours 23-08 are the night and 02-04 
are the Boost tariff. 

You can also optionally prefix this with a day range 1-7 to depict tariffs for specific days. 
For example:

    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223 Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 7-7:09-17:Free \

The above defines a Free tariff of 0. Then this tariff is applied only on Sunday between 9-5pm 

Lastly, the --annual_standing_charge value is yearly standing charge. 

See:
https://github.com/dresdner353/energyutils/blob/main/GEN_REPORT.md
for full documentation on the options available for this tool.

The whole point of this activity is to allow you customise the pricing to match your desired plan. The 
cost calculations then shown will closely match the actual costs you would be incurring. You can copy 
and paste this code section as many times as required to generate separate reports for different plans.

The only gap these calculations would have are things like PSO levies and other kinds of credits. 
