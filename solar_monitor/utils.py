import argparse
import requests
import json
import os
import sys
import traceback
import time
import datetime
import dateutil.parser
import zoneinfo

# global tracker for verbose logging
gv_verbose = 0

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
        sys.stdout.flush()

    return

