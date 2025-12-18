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
        verbose: bool,
        message: str
        ) -> None:

    if verbose:
        print(
                '%s %s' % (
                    time.asctime(), 
                    message
                    )
                )
        sys.stdout.flush()

    return


def thread_exception_wrapper(
        fn, 
        *args, 
        **kwargs):
    """
    This is a simple exception wrapper used for concurrent futures
    to capture the actual exception and then raise a new one with the 
    string detail of the original. Prevents loss of exception context
    when using concurrent futures
    """

    try:
        # call fn arg with other args
        return fn(*args, **kwargs)

    except Exception:
        # generate a formal backtrace as a string
        # and raise this as a new exception with that string as title
        exception_detail = sys.exc_info()
        exception_list = traceback.format_exception(
                *exception_detail,
                limit = 200)
        exception_str = ''.join(exception_list)

        raise Exception(exception_str)  
