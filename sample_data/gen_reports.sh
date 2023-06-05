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

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_24h.xlsx \
    --tariff_rate 24h:0.4819 \
    --tariff_interval 00-00:24h \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_standard_smart.xlsx \
    --tariff_rate Day:0.5149 Night:0.3802 Peak:0.6270 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_discount_weekend.xlsx \
    --tariff_rate Day:0.5071 Night:0.4534 Peak:0.6185 Weekend:0.4534\
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 6-7:00-00:Weekend \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_tou.xlsx \
    --tariff_rate Day:0.5196 Night:0.3743 Peak:0.6224 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_freetime_sat.xlsx \
    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223  Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 6-6:09-17:Free \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_freetime_sun.xlsx \
    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223  Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 7-7:09-17:Free \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file bge_report_ev.xlsx \
    --tariff_rate Day:0.4803 Night:0.3622 Peak:0.6697 EV:0.1224 \
    --tariff_interval 08-23:Day 23-08:Night 02-05:EV 1-5:17-19:Peak \
    --standing_rate 0.0478 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file sse_report_boost.xlsx \
    --tariff_rate Day:0.4830 Night:0.2735 Peak:0.6492 Boost:0.1055 \
    --tariff_interval 08-23:Day 23-08:Night 02-05:Boost 17-19:Peak \
    --standing_rate 0.0349 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file energia_report_smart.xlsx \
    --tariff_rate Day:0.4576 Night:0.2450 Peak:0.4794 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0270 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file energia_report_ev.xlsx \
    --tariff_rate Day:0.5262 Night:0.2817 Peak:0.5753 EV:0.1264 \
    --tariff_interval 08-23:Day 23-08:Night 02-06:EV 17-19:Peak \
    --standing_rate 0.0270 \
    --fit_rate 0.18
