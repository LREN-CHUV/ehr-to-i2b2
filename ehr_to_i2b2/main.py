#!/usr/bin/env python3.5

import logging
import argparse
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ehr_to_i2b2 import i2b2_connection
from ehr_to_i2b2 import clm_import
from ehr_to_i2b2 import edsd_import
from ehr_to_i2b2 import adni_import
from ehr_to_i2b2 import ppmi_import


def main(dataset, input_folder, i2b2_url):
    logging.info("Connecting to I2B2...")
    i2b2_conn = i2b2_connection.Connection(i2b2_url)

    if 'CLM' == dataset.upper():
        clm_import.process(input_folder, i2b2_conn, dataset)
    elif 'EDSD' == dataset.upper():
        edsd_import.process(input_folder, i2b2_conn, dataset)
    elif 'ADNI' == dataset.upper():
        adni_import.process(input_folder, i2b2_conn, dataset)
    elif 'PPMI' == dataset.upper():
        ppmi_import.process(input_folder, i2b2_conn, dataset)
    else:
        logging.info("Unknown dataset !")

    i2b2_conn.close()
    logging.info("I2B2 connection closed")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("input_folder")
    args_parser.add_argument("i2b2_url")
    args_parser.add_argument("dataset")
    args = args_parser.parse_args()
    main(args.dataset, args.input_folder, args.i2b2_url)
