#!/bin/bash
set -e

HDF_DIR='hdf_files'
HDF_DATA='hdf_data'
ESB_SCRIPT=../esb_hdf_reader.py
GEN_REPORT_SCRIPT=../gen_report.py
REPORTS='day week month year hour tariff 24h weekday'

# cd to path of script
SCRIPT_DIR=$(dirname "$(readlink -f $0)")
cd "${SCRIPT_DIR}"

mkdir -p "${HDF_DATA}"
rm -f "${HDF_DATA}"/*

# Read ESB HDF file and export JSONL files
python3 ${ESB_SCRIPT} \
    --file "${HDF_DIR}"/HDF*.csv  \
    --odir "${HDF_DATA}"

# Example EV report
python3 ${GEN_REPORT_SCRIPT} \
    --idir "${HDF_DATA}" \
    --file esb_report.xlsx \
    --reports ${REPORTS} \
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 \
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost \
    --annual_standing_charge 396 \
    --fit_rate 0.21 

