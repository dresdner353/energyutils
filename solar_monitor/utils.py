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


def wrap_exceptions(fn):
    """ Decorator to wrap a function and re-raise exceptions with full backtrace 
        as the exception raise message. Used to decorate functions submitted to 
        current.futures where the original traceback is lost.
    """

    def wrapper(*args, **kwargs):
        try:
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

    return wrapper 
