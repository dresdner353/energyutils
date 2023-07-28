HDF_DATA=hdf_data
REPORTS_DIR=reports
GEN_REPORT_SCRIPT=../gen_report.py
REPORTS='year tariff month week day hour'

mkdir -p ${HDF_DATA}
rm -f ${HDF_DATA}/*
mkdir -p ${REPORTS_DIR}
rm -f ${REPORTS_DIR}/*

# parse ESB data into separate JSONL files per day
python3 ../esb_hdf_reader.py --file HDF_example.csv  --odir ${HDF_DATA}

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_24h.xlsx \
    --reports ${REPORTS} \
    --tariff_rate 24h:0.4327 \
    --tariff_interval 00-00:24h \
    --standing_rate 0.0346 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_nightsaver.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4230 Night:0.2280 \
    --tariff_interval 09-00:Day 00-09:Night \
    --standing_rate 0.0453 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_electricplus.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4451 Night:0.2339 Peak:0.4746 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0346 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_electricboost_rural.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4368 Night:0.2155 Boost:0.1265 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --standing_rate 0.0552 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_dualplus.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4310 Night:0.2265 Peak:0.4596 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0346 \
    --fit_rate 0.21 

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_dualboost.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --standing_rate 0.0453 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_sat_free.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4346 Night:0.4346 Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 6-6:08-23:Free \
    --standing_rate 0.0346 \
    --fit_rate 0.21
    
python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/ei_report_sun_free.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4346 Night:0.4346 Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 7-7:08-23:Free \
    --standing_rate 0.0346 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_24h.xlsx \
    --reports ${REPORTS} \
    --tariff_rate 24h:0.4819 \
    --tariff_interval 00-00:24h \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_standard_smart.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5149 Night:0.3802 Peak:0.6270 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_discount_weekend.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5071 Night:0.4534 Peak:0.6185 Weekend:0.4534\
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 6-7:00-00:Weekend \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_tou.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5196 Night:0.3743 Peak:0.6224 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_freetime_sat.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223  Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 6-6:09-17:Free \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_freetime_sun.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223  Free:0 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 7-7:09-17:Free \
    --standing_rate 0.0321 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_ev.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4803 Night:0.3622 Peak:0.6697 EV:0.1224 \
    --tariff_interval 08-23:Day 23-08:Night 02-05:EV 1-5:17-19:Peak \
    --standing_rate 0.0478 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/bge_report_ev_rural.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4322 Night:0.3260 Peak:0.6027 EV:0.1102 \
    --tariff_interval 08-23:Day 23-08:Night 02-05:EV 1-5:17-19:Peak \
    --standing_rate 0.0478 \
    --fit_rate 0.185

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/sse_report_boost.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4830 Night:0.2735 Peak:0.6492 Boost:0.1055 \
    --tariff_interval 08-23:Day 23-08:Night 02-05:Boost 17-19:Peak \
    --standing_rate 0.0349 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/sse_report_smart.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4532 Night:0.2940 Peak:0.5727 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0275 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/sse_report_nightsaver.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4434 Night:0.2752 \
    --tariff_interval 09-00:Day 00-09:Night \
    --standing_rate 0.0353 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/energia_report_smart.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4576 Night:0.2450 Peak:0.4794 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0270 \
    --fit_rate 0.24

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/energia_report_ev.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.5262 Night:0.2817 Peak:0.5753 EV:0.1264 \
    --tariff_interval 08-23:Day 23-08:Night 02-06:EV 17-19:Peak \
    --standing_rate 0.0270 \
    --fit_rate 0.18

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/flogas_report_smart.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.3680 Night:0.2868 Peak:0.4352 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0387 \
    --fit_rate 0.20

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/pinergy_report_work_from_home.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Work:0.3263 Peak:0.4662 \
    --tariff_interval 09-17:Work 17-09:Peak \
    --standing_rate 0.0324 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/pinergy_report_family_time.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Evening:0.2797 Peak:0.4662 \
    --tariff_interval 19-00:Evening 00-19:Peak \
    --standing_rate 0.0324 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/pinergy_report_ev.xlsx \
    --reports ${REPORTS} \
    --tariff_rate EV:0.0692 Peak:0.4662 \
    --tariff_interval 02-05:EV 05-02:Peak \
    --standing_rate 0.0324 \
    --fit_rate 0.21

python3 ${GEN_REPORT_SCRIPT} \
    --idir ${HDF_DATA} \
    --file ${REPORTS_DIR}/pinergy_report_standard_smart.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4646 Night:0.3546 Peak:0.4992 \
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak \
    --standing_rate 0.0324 \
    --fit_rate 0.21

