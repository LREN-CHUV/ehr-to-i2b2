#!/usr/bin/env python3.5

import logging
import argparse
import os
import sys

from pandas import read_excel
from glob import iglob
from datetime import datetime

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ehr_to_i2b2 import i2b2_connection
from ehr_to_i2b2 import util


DEFAULT_DATE = datetime(1, 1, 1)


def process_clm(input_folder, i2b2_conn, dataset):
    logging.info("Importing scores (neuropsychological scores)...")
    for scores_path in iglob(os.path.join(input_folder, '**/Scores_*.xls'), recursive=True):
        data = read_excel(scores_path)
        for _, row in data.iterrows():
            encounter_num = i2b2_conn.get_encounter_num(
                row['EVENT_ID'], dataset, dataset, row['SUBJECT_ID'], dataset)
            patient_num = i2b2_conn.get_patient_num(row['SUBJECT_ID'], dataset, dataset)
            patient_age = util.compute_age(row['SUBJ_AGE_YEARS'], row['SUBJ_AGE_MONTHS'])
            i2b2_conn.save_patient(patient_num)
            i2b2_conn.save_visit(encounter_num, patient_num, patient_age=patient_age)
            concept_shortname = row['TEST_CODE']
            concept_cd = dataset + ":" + concept_shortname
            name_char = row['TEST_NAME']
            concept_path = os.path.join("/", dataset, 'scores', concept_shortname)
            i2b2_conn.save_concept(concept_path, concept_cd=concept_cd, concept_fullname=name_char)
            val = row['TEST_VALUE']
            valtype_cd = util.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            start_date = DEFAULT_DATE
            i2b2_conn.save_observation(
                encounter_num, concept_cd, dataset, start_date, patient_num, valtype_cd, tval_char, nval_num)

    logging.info("Importing events (patient age at event time-point)...")
    for events_path in iglob(os.path.join(input_folder, '**/Events_*.xls'), recursive=True):
        data = read_excel(events_path)
        for _, row in data.iterrows():
            encounter_num = i2b2_conn.get_encounter_num(
                row['ID_EVENT'], dataset, dataset, row['SUBJECT_CODE'], dataset)
            patient_num = i2b2_conn.get_patient_num(row['SUBJECT_CODE'], dataset, dataset)
            patient_age = util.compute_age(row['EVENT_SUBJ_AGE_YEARS'], row['EVENT_SUBJ_AGE_MONTHS'])
            i2b2_conn.save_patient(patient_num)
            i2b2_conn.save_visit(encounter_num, patient_num, patient_age=patient_age)

    logging.info("Importing demographics (patient sex)...")
    for demographics_path in iglob(os.path.join(input_folder, '**/Demographics_*.xls'), recursive=True):
        data = read_excel(demographics_path)
        for _, row in data.iterrows():
            subject_num = i2b2_conn.get_patient_num(row['SUBJECT_CODE'], dataset, dataset)
            subject_sex = util.normalize_sex(row['SEX'])
            i2b2_conn.save_patient(subject_num, sex_cd=subject_sex)

    logging.info("Importing diagnostics (ICD-10 diagnostics, etc)...")
    for diagcats_path in iglob(os.path.join(input_folder, '**/DiagCats_*.xls'), recursive=True):
        data = read_excel(diagcats_path)
        for _, row in data.iterrows():
            pass
            # TODO: implement

    logging.info("Importing diagnosis categories (diagnostics categories)...")
    for diagcats_path in iglob(os.path.join(input_folder, '**/DiagCats_*.xls'), recursive=True):
        data = read_excel(diagcats_path)
        for _, row in data.iterrows():
            pass
            # TODO: implement

    # TODO: import Morphobox


def process_edsd(input_folder, i2b2_conn, dataset):
    logging.info("EHR importation for EDSD dataset is not available yet !")


def process_adni(input_folder, i2b2_conn, dataset):
    logging.info("EHR importation for ADNI dataset is not available yet !")


def process_ppmi(input_folder, i2b2_conn, dataset):
    logging.info("EHR importation for PPMI dataset is not available yet !")


def main(dataset, input_folder, i2b2_url):
    logging.info("Connecting to I2B2...")
    i2b2_conn = i2b2_connection.Connection(i2b2_url)

    if 'CLM' == dataset.upper():
        process_clm(input_folder, i2b2_conn, dataset)
    elif 'EDSD' == dataset.upper():
        process_edsd(input_folder, i2b2_conn, dataset)
    elif 'ADNI' == dataset.upper():
        process_edsd(input_folder, i2b2_conn, dataset)
    elif 'PPMI' == dataset.upper():
        process_edsd(input_folder, i2b2_conn, dataset)
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
