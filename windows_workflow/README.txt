Steps to get your ESB report generating:

* Install Python3
----------------------------------------------------------------------------
Launch the Microsoft Store and search for python3. 
Install by clicking the "Get" button


* Run initial setup script
----------------------------------------------------------------------------
In this folder, double-click the batch script called "init_setup".

Note:You may be warned about this as being an unknown program and feel free to 
virus scan etc. But depending on your virus scanner etc, you may have to 
Click on a "Run anyway" to kick it off. Windows Defender will popup a dialog with 
button "Don't run", but to run it, you click on the "More info" link and there is a 
"Run anyway" option to launch it.

This script only runs Python3 and install required modules for 
the report scripts. 


* Put the ESB HDF file in place
----------------------------------------------------------------------------
Download your latest ESB HDF file and drop it into 
this folder and rename as esb_hdf.csv. You can also work with 
the sample file that is included to start if preferred and delete it later on once
you have your own HDF file. 


* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, double-click on "gen_esb_report". This should parse out data from the 
ESB HDF file and then generate report files in the same directory 

Note: You will likely get the same warnings before running this script as above
