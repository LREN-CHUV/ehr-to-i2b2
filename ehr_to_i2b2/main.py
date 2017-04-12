#!/usr/bin/env python3.5

import logging
import argparse
import os
import sys

from pandas import read_excel
from glob import iglob

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ehr_to_i2b2 import i2b2_connection


def process_clm(input_folder, i2b2_conn):
    logging.info("Importing demographics...")
    for demographics_path in iglob(os.path.join(input_folder, '**/Demographics_*.xls'), recursive=True):
        data = read_excel(demographics_path)
        for _, row in data.iterrows():
            subject_id = row['SUBJECT_CODE']
            subject_sex = row['SEX']

            # TODO: Insert those data into I2B2
    # TODO: Do the same for other EHR files


def process_edsd(input_folder, i2b2_conn):
    logging.info("EHR importation for EDSD dataset is not available yet !")


def process_adni(input_folder, i2b2_conn):
    logging.info("EHR importation for ADNI dataset is not available yet !")


def process_ppmi(input_folder, i2b2_conn):
    logging.info("EHR importation for PPMI dataset is not available yet !")


def main(dataset, input_folder, i2b2_url):
    logging.info("Connecting to I2B2...")
    i2b2_conn = i2b2_connection.Connection(i2b2_url)

    if 'CLM' == dataset.upper():
        process_clm(input_folder, i2b2_conn)
    elif 'EDSD' == dataset.upper():
        process_edsd(input_folder, i2b2_conn)
    elif 'ADNI' == dataset.upper():
        process_edsd(input_folder, i2b2_conn)
    elif 'PPMI' == dataset.upper():
        process_edsd(input_folder, i2b2_conn)
    else:
        logging.info("Unknown dataset !")

    i2b2_conn.close()
    logging.info("I2B2 connection closed")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("dataset")
    args_parser.add_argument("input_folder")
    args_parser.add_argument("i2b2_url")
    args = args_parser.parse_args()
    main(args.dataset, args.input_folder, args.i2b2_url)
