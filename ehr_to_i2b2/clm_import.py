import logging
import os

from glob import iglob
from pandas import read_excel

from . import util


def process(input_folder, i2b2_conn, dataset):
    logging.info("Importing scores (neuropsychological scores, etc)...")
    import_scores(dataset, i2b2_conn, input_folder)

    logging.info("Importing events (patient age at event time-point)...")
    import_events(dataset, i2b2_conn, input_folder)

    logging.info("Importing demographics (patient sex)...")
    import_demographics(dataset, i2b2_conn, input_folder)

    logging.info("Importing diagnosis categories...")
    import_diagcat(dataset, i2b2_conn, input_folder)

    logging.info("Importing ICD10 diagnosis...")
    import_icd10(dataset, i2b2_conn, input_folder)

    logging.info("Importing morphobox...")
    import_morphobox(dataset, i2b2_conn, input_folder)


def import_scores(dataset, i2b2_conn, input_folder):
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
            concept_path = os.path.join("/", dataset, 'EHR', 'Scores', concept_shortname)
            i2b2_conn.save_concept(concept_path, concept_cd=concept_cd, concept_fullname=name_char)
            val = row['TEST_VALUE']
            valtype_cd = util.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            start_date = util.DEFAULT_DATE
            i2b2_conn.save_observation(
                encounter_num, concept_cd, dataset, start_date, patient_num, valtype_cd, tval_char, nval_num)


def import_events(dataset, i2b2_conn, input_folder):
    for events_path in iglob(os.path.join(input_folder, '**/Events_*.xls'), recursive=True):
        data = read_excel(events_path)
        for _, row in data.iterrows():
            encounter_num = i2b2_conn.get_encounter_num(
                row['ID_EVENT'], dataset, dataset, row['SUBJECT_CODE'], dataset)
            patient_num = i2b2_conn.get_patient_num(row['SUBJECT_CODE'], dataset, dataset)
            patient_age = util.compute_age(row['EVENT_SUBJ_AGE_YEARS'], row['EVENT_SUBJ_AGE_MONTHS'])
            i2b2_conn.save_patient(patient_num)
            i2b2_conn.save_visit(encounter_num, patient_num, patient_age=patient_age)


def import_demographics(dataset, i2b2_conn, input_folder):
    for demographics_path in iglob(os.path.join(input_folder, '**/Demographics_*.xls'), recursive=True):
        data = read_excel(demographics_path)
        for _, row in data.iterrows():
            subject_num = i2b2_conn.get_patient_num(row['SUBJECT_CODE'], dataset, dataset)
            subject_sex = util.normalize_sex(row['SEX'])
            i2b2_conn.save_patient(subject_num, sex_cd=subject_sex)


def import_diagcat(dataset, i2b2_conn, input_folder):
    for diagcats_path in iglob(os.path.join(input_folder, '**/DiagCats_*.xls'), recursive=True):
        data = read_excel(diagcats_path)
        concept_path = os.path.join("/", dataset, 'EHR', 'Diagnosis', 'Diag Category')
        concept_cd = dataset + ":diag_category"
        name_char = "Diag Category"
        i2b2_conn.save_concept(concept_path, concept_cd=concept_cd, concept_fullname=name_char)
        for _, row in data.iterrows():
            patient_ide = row['SUBJECT_CODE']
            patient_age = util.compute_age(row['SUBJ_AGE_YEARS'], row['SUBJ_AGE_MONTHS'])
            diag = row['DIAG_CATEGORY']
            patient_num = i2b2_conn.get_patient_num(patient_ide, dataset, dataset)
            visits = i2b2_conn.db_session.query(i2b2_conn.VisitDimension.encounter_num).filter_by(
                patient_num=patient_num, patient_age=patient_age).all()
            for visit in visits:
                encounter_num = visit[0]
                start_date = util.DEFAULT_DATE
                valtype_cd = util.find_type(diag)
                if valtype_cd == 'N':
                    tval_char = 'E'
                    nval_num = float(diag)
                else:
                    tval_char = diag
                    nval_num = None
                i2b2_conn.save_observation(
                    encounter_num, concept_cd, dataset, start_date, patient_num, valtype_cd, tval_char, nval_num)


def import_icd10(dataset, i2b2_conn, input_folder):
    for diagnostics_path in iglob(os.path.join(input_folder, '**/Diagnostics_*.xls'), recursive=True):
        data = read_excel(diagnostics_path)
        for _, row in data.iterrows():
            encounter_ide = row['ID_EVENT']
            patient_ide = row['SUBJ_CODE']
            icd10 = row['DIAG_ICD10']
            # TODO: store fullname in lookup table -> icd10_fullname = row['DIAG_ICD10_FULL']
            encounter_num = i2b2_conn.get_encounter_num(encounter_ide, dataset, dataset, patient_ide, dataset)
            patient_num = i2b2_conn.get_patient_num(patient_ide, dataset, dataset)
            concept_cd = dataset + ':icd10'
            concept_path = os.path.join('/', dataset, 'EHR', 'Diagnosis', 'ICD10')
            i2b2_conn.save_concept(concept_path, concept_cd=concept_cd, concept_fullname="ICD 10")
            i2b2_conn.save_observation(
                encounter_num, concept_cd, dataset, util.DEFAULT_DATE, patient_num, 'T', icd10, None)


def import_morphobox(dataset, i2b2_conn, input_folder):
    logging.info("Not implemented yet...")
    # TODO: implement it
