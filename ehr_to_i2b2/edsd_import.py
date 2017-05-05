import logging
import pandas

from glob import iglob
from os.path import join

from sqlalchemy.orm.exc import MultipleResultsFound

from . import util


EHR_FILENAME = "EDSD-multicenter.csv"
SEPARATOR = ";"

INTERESTING_COLUMNS = ["PatientID", "Age", "Gender", "Handedness", "Patient'sBirthDate", "Diagnosis", "MMSE_TOT",
                       "MagneticFieldStrength", "center", "mri_date", "MMSE_date"]


def process(input_folder, i2b2_conn, dataset):
    ehr_file_path = next(iglob(join(input_folder, '**/' + EHR_FILENAME), recursive=True))
    df = pandas.read_csv(ehr_file_path, sep=SEPARATOR, low_memory=False)
    df = df[INTERESTING_COLUMNS]
    df.drop_duplicates(inplace=True)

    for _, row in df.iterrows():
        patient_ide = row['PatientID']
        logging.info("Importing EHR for %s", patient_ide)

        try:
            gender = util.normalize_sex(row['Gender'])
        except ValueError:
            gender = None
        birthdate = util.normalize_date(row["Patient'sBirthDate"])
        patient_num = i2b2_conn.get_patient_num(patient_ide, dataset, dataset)
        i2b2_conn.save_patient(patient_num, gender, birthdate)

        mri_date = util.normalize_date(row['mri_date'])
        encounter_ide = _find_visit(i2b2_conn, patient_ide, mri_date)
        if encounter_ide:
            logging.info("-> found visit %s", encounter_ide)

            try:
                location = row['center']
            except ValueError:
                location = None
            try:
                diagnosis = row['Diagnosis']
            except ValueError:
                diagnosis = None
            try:
                age = float(row['Age'])
            except ValueError:
                age = None
            try:
                mmse_score = row['MMSE_TOT']
            except ValueError:
                mmse_score = None
            try:
                magnetic_field_strength = row['MagneticFieldStrength']
            except ValueError:
                magnetic_field_strength = None

            encounter_num = i2b2_conn.get_encounter_num(encounter_ide, dataset, dataset, patient_ide, dataset)
            i2b2_conn.save_visit(
                encounter_num, patient_num, patient_age=age, start_date=mri_date, location_cd=location)

            _save_observation(i2b2_conn, dataset, patient_num, encounter_num, "diag_category", 'Diag Category',
                              join('EHR', 'Diagnosis', 'Diag Category'), diagnosis)

            if mmse_score:
                _save_observation(i2b2_conn, dataset, patient_num, encounter_num, "MMSE", 'Mini Mental State',
                                  join('EHR', 'Scores', 'MMSE'), mmse_score)

            if magnetic_field_strength:
                _save_observation(
                    i2b2_conn, dataset, patient_num, encounter_num, "MagneticFieldStrength", "Magnetic Field Strength",
                    join('Imaging Data', 'Acquisition Settings', 'MagneticFieldStrength'), magnetic_field_strength)
        else:
            logging.warning("Cannot find visit for patient %s and date %s", patient_ide, str(mri_date))


def _save_observation(i2b2_conn, dataset, patient_num, encounter_num, shortname, fullname, path_postfix, value):
    start_date = util.DEFAULT_DATE
    concept_cd = dataset + ":" + shortname
    concept_fullname = fullname
    concept_path = join("/", dataset, path_postfix)
    valtype_cd = util.find_type(value)
    if valtype_cd == 'N':
        tval_char = 'E'
        nval_num = float(value)
    else:
        tval_char = value
        nval_num = None
    i2b2_conn.save_concept(concept_path, concept_cd=concept_cd, concept_fullname=concept_fullname)
    i2b2_conn.save_observation(encounter_num, concept_cd, dataset, start_date, patient_num, valtype_cd, tval_char,
                               nval_num)


def _find_visit(i2b2_conn, patient_ide, mri_date):
    try:
        return i2b2_conn.db_session.query(i2b2_conn.EncounterMapping.encounter_num).\
            filter_by(patient_ide=patient_ide).one_or_none()
    except MultipleResultsFound:
        encounter_num = None
        if mri_date:
            # TODO: try to get visit matching mri_date
            pass
        if not encounter_num:
            return i2b2_conn.db_session.query(i2b2_conn.EncounterMapping.encounter_num).\
                filter_by(patient_ide=patient_ide).first()
