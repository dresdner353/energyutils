#!/bin/bash
set -e

SOLIS_DATA='solis_data'
SOLIS_SCRIPT=../solis_data_util.py
GEN_REPORT_SCRIPT=../gen_report.py
TARIFF_PLANS=../sample_tariffs_plan.json
REPORTS='day week month year hour tariff 24h weekday'

# Solis API
SOLIS_API_HOST=https://www.soliscloud.com:PPPPP
SOLIS_KEY_ID=XXXXXXXXXXXXXXXXXXX
SOLIS_KEY_SECRET=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
SOLIS_INVERTER_SN=ZZZZZZZZZZZZZZZZ
SOLIS_STRINGS=0 

# Shelly API config
# Note: uncomment shelly_xxxxx lines below if using
# a Shelly device in conjunction with the Solis inverter
SHELLY_API_HOST=example.com
SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SHELLY_DEVICE_ID=000000000000

mkdir -p "${SOLIS_DATA}"

# Retrieve data from Solis Cloud
python3 ${SOLIS_SCRIPT} \
    --odir "${SOLIS_DATA}" \
    --days 30 \
    --solis_api_host ${SOLIS_API_HOST} \
    --solis_key_id ${SOLIS_KEY_ID} \
    --solis_key_secret ${SOLIS_KEY_SECRET}  \
    --solis_inverter_sn ${SOLIS_INVERTER_SN} \
    --solis_strings ${SOLIS_STRINGS} \
    #--shelly_api_host ${SHELLY_API_HOST} \
    #--shelly_device_id ${SHELLY_DEVICE_ID} \
    #--shelly_auth_key ${SHELLY_AUTH_KEY} \

# Example EV report
python3 ${GEN_REPORT_SCRIPT} \
    --idir "${SOLIS_DATA}" \
    --file solis_report.xlsx \
    --reports ${REPORTS} \
    --tariffs "${TARIFF_PLANS}" 

