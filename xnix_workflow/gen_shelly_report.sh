#!/bin/bash
set -e

SHELLY_DATA='shelly_data'
SHELLY_SCRIPT=../shelly_em_data_util.py
GEN_REPORT_SCRIPT=../gen_report.py
REPORTS='day week month year hour tariff 24h weekday'

# Shelly API config
SHELLY_HOST=example.com
SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SHELLY_DEVICE_ID=000000000000

mkdir -p "${SHELLY_DATA}"

# Retrieve data from Shelly Cloud
python3 ${SHELLY_SCRIPT} \
    --host ${SHELLY_HOST} \
    --id ${SHELLY_DEVICE_ID} \
    --auth_key ${SHELLY_AUTH_KEY} \
    --odir "${SHELLY_DATA}" \
    --days 30 

# Example EV report
python3 ${GEN_REPORT_SCRIPT} \
    --idir "${SHELLY_DATA}" \
    --file shelly_report.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --annual_standing_charge 396 \
    --fit_rate 0.21 

