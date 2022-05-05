import pandas as pd
from utils import read_blob, write_blob

# Set values that specify a blob to load.
STORAGE_ACCOUNT_URL = "https://pitestdatasa.blob.core.windows.net"
CONTAINER_NAME = "bronze"
CASE_DATAMART_FILENAME = "CSVS/datamarts/covid_case_datamart.csv"
VAX_DATAMART_FILENAME = "CSVS/datamarts/covid_vaccine_datamart.csv"
BREAKTHROUGH_DATAMART_FILENAME = "CSVS/datamarts/covid_breakthrough_datamart.csv"

# Read data
cases = pd.read_csv(
    read_blob(STORAGE_ACCOUNT_URL, CONTAINER_NAME, CASE_DATAMART_FILENAME)
)
cases.drop(
    columns=[
        "standardizedFirstName",
        "standardizedLastName",
        "standardizedPhone",
        "standardizedAddress",
    ],
    inplace=True,
)
vax_status = pd.read_csv(
    read_blob(STORAGE_ACCOUNT_URL, CONTAINER_NAME, VAX_DATAMART_FILENAME),
    usecols=["patientHash", "vaccinationDate", "boosterDate"],
)

# Generate vaccine breakthrough datamart and compute basic summary stats
breakthrough_datamart = pd.merge(cases, vax_status, how="left", on="patientHash")
num_cases = len(cases)
num_patients_with_vax_records = len(vax_status)
num_patients_shared = len(pd.merge(cases, vax_status, how="inner", on="patientHash"))
num_breakthrough_cases = len(
    breakthrough_datamart[
        breakthrough_datamart.effectiveDateTime > breakthrough_datamart.vaccinationDate
    ]
)

# Write datamart to blob storage.
write_blob(
    breakthrough_datamart.to_csv(encoding="utf-8", index=False),
    STORAGE_ACCOUNT_URL,
    CONTAINER_NAME,
    BREAKTHROUGH_DATAMART_FILENAME,
)
full_path = (
    STORAGE_ACCOUNT_URL + "/" + CONTAINER_NAME + "/" + BREAKTHROUGH_DATAMART_FILENAME
)
print(f"COVID vaccine breakthrough datamart saved to: {full_path}")
print(
    f"""Quick Summary:
        Total Cases Identified:  {num_cases}
        Number of patients with vax records: {num_patients_with_vax_records}
        Number of patients present in both datasets: {num_patients_shared}
        Number of breakthrough cases identified: {num_breakthrough_cases}"""
)
