import pandas

from glob import iglob
from os.path import join


EHR_FILENAME = "EDSD-multicenter.csv"
SEPARATOR = ";"

INTERESTING_COLUMNS = ["PatientID", "Age", "Gender", "Handedness", "Patient'sBirthDate", "Diagnosis", "MMSE_TOT",
                       "MagneticFieldStrength", "center", "mri_date", "MMSE_date"]


def process(input_folder, i2b2_conn, dataset):
    ehr_file_path = next(iglob(join(input_folder, '**/' + EHR_FILENAME), recursive=True))
    df = pandas.read_csv(ehr_file_path, sep=SEPARATOR, low_memory=False)
    df = df[INTERESTING_COLUMNS]
