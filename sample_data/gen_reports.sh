HDF_DATA=/tmp/hdf_data
GEN_REPORT_SCRIPT=../gen_report.py

mkdir -p ${HDF_DATA}
rm -f ${HDF_DATA}/*

# parse ESB data into separate JSONL files per day
python3 ../esb_hdf_reader.py --file HDF_example.csv  --odir ${HDF_DATA}

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ei_report_24h.xlsx \
    --tariff_rate 24h:0.3959 \
    --tariff_interval 00-00:24h \
    --standing_rate 0.0346 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ei_report_dualplus.xlsx \
    --tariff_rate Day:0.4310 Night:0.2265 Peak:0.4596 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0346 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ei_report_dualboost.xlsx \
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --standing_rate 0.0453 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ei_report_sat_free.xlsx \
    --tariff_rate Day:0.4346 Night:0.4346 Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 6-6:08-23:Free \
    --standing_rate 0.0346 \
    --fit_rate 0.21
    
python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ei_report_sun_free.xlsx \
    --tariff_rate Day:0.4346 Night:0.4346 Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 7-7:08-23:Free \
    --standing_rate 0.0346 \
    --fit_rate 0.21
