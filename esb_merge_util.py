import argparse
import requests
import json
import os
import time
import datetime
import dateutil.parser
import zoneinfo


def log_message(
        verbose,
        message):

    if verbose:
        print(
                '%s %s' % (
                    time.asctime(), 
                    message
                    )
                )

    return


def load_jsonl_file(filename):
    data_dict = {}

    with open(filename) as fp:
        for line in fp:
            rec = json.loads(line)
            data_dict[rec['ts']] = rec

    return data_dict


# main()

parser = argparse.ArgumentParser(
        description = 'ESB Data Merge Utility'
        )

parser.add_argument(
        '--inverter_dir', 
        help = 'Input Directory for inverter files', 
        required = True
        )

parser.add_argument(
        '--esb_dir', 
        help = 'Input Directory for ESB files', 
        required = True
        )

parser.add_argument(
        '--odir', 
        help = 'Output Directory for generated files', 
        required = True
        )

parser.add_argument(
        '--verbose', 
        help = 'Enable verbose output', 
        action = 'store_true'
        )

args = vars(parser.parse_args())
inverter_dir = args['inverter_dir']
esb_dir = args['esb_dir']
odir = args['odir']
gv_verbose = args['verbose']

# JSON encoder force decimal places to 5
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.5f'))

json.encoder.c_make_encoder = None
json.encoder.float = RoundingFloat

if not os.path.exists(odir):
    os.mkdir(odir)

# simple protection on director values
if len(set([inverter_dir, esb_dir, odir])) != 3:
    log_message(gv_verbose, 'Error: Directories must be unique')
    sys.exit(-1)


# read each file in inverter dir
for filename in sorted(os.listdir(inverter_dir)):
    # only loading .jsonl files
    if not filename.endswith('.jsonl'):
        continue

    # test for ESB equivaent
    inverter_filename = os.path.join(inverter_dir, filename)
    esb_filename = os.path.join(esb_dir, filename)
    merge_filename = os.path.join(odir, filename)

    # load inverter data
    inverter_dict = load_jsonl_file(inverter_filename)

    # load and merge ESB data is present
    context = 'No ESB data'
    if os.path.exists(esb_filename):
        esb_dict = load_jsonl_file(esb_filename)
        context = 'Merged with ESB data'

        # merge data
        for ts in inverter_dict:
            if ts in esb_dict:
                inverter_rec = inverter_dict[ts]
                esb_rec = esb_dict[ts]

                # direct overwrite of the import/export values
                inverter_rec['import'] = esb_rec['import']
                inverter_rec['export'] = esb_rec['export']

                # solar_consumed and consumed recalcs
                if 'solar' in inverter_rec:
                    inverter_rec['solar_consumed'] = inverter_rec['solar'] - inverter_rec['export']
                    inverter_rec['consumed'] = inverter_rec['import'] + inverter_rec['solar_consumed']

    log_message(1, 'Writing %s (%s)' % (merge_filename, context))
    with open(merge_filename, 'w') as f:
        for key in sorted(inverter_dict.keys()):
            f.write(json.dumps(inverter_dict[key]) + '\n')
