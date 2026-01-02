#!/bin/bash
#set -e
set -e

HDF_PATH='esb_hdf'
ESB_DATA='esb_data'
BATTERY_DATA='battery_data'
REPORTS='reports'
SMART_TARIFF_PLAN=../sample_tariffs_plan.json
EV_TARIFF_PLAN=../sample_tariffs_ev_plan.json
ESB_SCRIPT=../esb_hdf_reader.py
BATTERY_SIM_SCRIPT=../battery_sim.py
GEN_REPORT_SCRIPT=../gen_report.py

mkdir -p "${ESB_DATA}"
rm -f "${ESB_DATA}"/*

mkdir -p "${BATTERY_DATA}"
rm -f "${BATTERY_DATA}"/*

mkdir -p "${REPORTS}"
rm -f "${REPORTS}"/*

START=20230101
END=20241231

# EV grid shift and discharge bypass intervals
EV_GRID_SHIFT_INTERVAL="02-06"
EV_DISCHARGE_BYPASS_INTERVAL="02-06"

# reference data (no battery)
# --partial_days \
python3 ${ESB_SCRIPT} \
    --file "${HDF_PATH}"/HDF*.csv  \
    --partial_days \
    --odir "${ESB_DATA}"
    
# no battery smart plan
python3 ${GEN_REPORT_SCRIPT} \
    --idir "${ESB_DATA}" \
    --file "${REPORTS}"/no_battery_smart_plan.xlsx \
    --tariffs "${SMART_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}

# no battery with EV plan
# not of any use as this ends up costing too much sometimes
python3 ${GEN_REPORT_SCRIPT} \
    --idir "${ESB_DATA}" \
    --file "${REPORTS}"/no_battery_ev_plan.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}




# ################################################
# 5 kWh 
# ################################################
 
# 5kwh grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 5 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 2.5 \
    --discharge_rate 2.5 \
    --discharge_bypass_interval ${EV_DISCHARGE_BYPASS_INTERVAL} \
    --grid_shift_interval ${EV_GRID_SHIFT_INTERVAL}

python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/5kwh_gs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}

# 5kwh no grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 5 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 2.5 \
    --discharge_rate 2.5 

python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/5kwh_nogs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}






# ################################################
# 10 kWh 
# ################################################

# 10kwh grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 10 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 5 \
    --discharge_rate 5 \
    --discharge_bypass_interval ${EV_DISCHARGE_BYPASS_INTERVAL} \
    --grid_shift_interval ${EV_GRID_SHIFT_INTERVAL}


python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/10kwh_gs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}

# 10kwh no grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 10 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 5 \
    --discharge_rate 5 

python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/10kwh_nogs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}


# ################################################
# 15 kWh 
# ################################################

# 15kwh grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 15 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 5 \
    --discharge_rate 5 \
    --discharge_bypass_interval ${EV_DISCHARGE_BYPASS_INTERVAL} \
    --grid_shift_interval ${EV_GRID_SHIFT_INTERVAL}


python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/15kwh_gs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}

# 15kwh no grid shift
python3 ${BATTERY_SIM_SCRIPT} \
    --idir "${ESB_DATA}" \
    --odir "${BATTERY_DATA}" \
    --battery_capacity 15 \
    --max_charge_percent 100 \
    --min_charge_percent 10 \
    --charge_rate 5 \
    --discharge_rate 5 

python3 ${GEN_REPORT_SCRIPT} \
    --idir "${BATTERY_DATA}" \
    --file "${REPORTS}"/15kwh_nogs.xlsx \
    --tariffs "${EV_TARIFF_PLAN}" \
    --start ${START} \
    --end ${END}


