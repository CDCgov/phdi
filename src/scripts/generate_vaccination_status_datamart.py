import pandas as pd
import pathlib
import datetime
from utils import read_blob, record_combination_func, write_blob
from tqdm import tqdm


def determine_covid_vax_status(patient_immunizations: pd.DataFrame) -> pd.Series:
    """
    Given a patient's COVID immunizations records return a pandas series containing the
    patient's demographics and the dates when they:
        1.  Completed an initial COVID vaccination sequence.
        2.  Received a booster.
    When either of these dates cannot be determined return null.
    """
    vax_codes = {
        "jj_adult_initial": [212],
        "moderna_adult": [207],
        "pfizer_adult": [208, 217],
        "pfizer_pediatric": [218],
        "adult_boosters": [207, 221, 208, 217],
        "pfizer_12to17_boosters": [208, 217],
    }

    vax_sequence_specs = {
        "moderna_range": range(28, 56 + 1),
        "pfizer_range": range(21, 56 + 1),
        "jj_booster_delay": 56,
        "moderna_booster_delay": 150,
        "pfizer_booster_delay": 150,
    }

    patient_immunizations.sort_values(by=["occurrenceDateTime"], ascending=True)
    vaccinated_date = pd.NaT
    boosted_date = pd.NaT
    initial_vax_type = ""
    for idx, vaccination in patient_immunizations.iterrows():

        current_dose_age = (
            vaccination.occurrenceDateTime - vaccination.birthDate
        ).days / 365.25

        if pd.isnull(vaccinated_date):
            # J&J ages 18+
            if (
                vaccination.vaccineCode in vax_codes["jj_adult_initial"]
                and current_dose_age >= 18
            ):
                vaccinated_date = vaccination.occurrenceDateTime + datetime.timedelta(
                    days=14
                )
                initial_vax_type = "jj"
                next_dose_idx = idx + 1

            # Moderna ages 18+
            elif (
                vaccination.vaccineCode in vax_codes["moderna_adult"]
                and current_dose_age >= 18
            ):
                vaccinated_date = check_mrna_status(
                    idx,
                    patient_immunizations,
                    vax_codes["moderna_adult"],
                    vax_sequence_specs["moderna_range"],
                )
                initial_vax_type = "moderna"
                next_dose_idx = idx + 2

            # Pfizer ages 12 +
            elif (
                vaccination.vaccineCode in vax_codes["pfizer_adult"]
                and current_dose_age > 12
            ):
                vaccinated_date = check_mrna_status(
                    idx,
                    patient_immunizations,
                    vax_codes["pfizer_adult"],
                    vax_sequence_specs["pfizer_range"],
                )
                initial_vax_type = "pfizer"
                next_dose_idx = idx + 2

            # Pfizer ages 5 to <12
            elif vaccination.vaccineCode in vax_codes[
                "pfizer_pediatric"
            ] and current_dose_age in range(5, 12):
                vaccinated_date = check_mrna_status(
                    idx,
                    patient_immunizations,
                    vax_codes["pfizer_pediatric"],
                    vax_sequence_specs["pfizer_range"],
                )
                initial_vax_type = "pfizer"
                next_dose_idx = idx + 2

        # Check for booster
        if pd.notnull(vaccinated_date) and len(patient_immunizations) > next_dose_idx:
            current_dose_age = (
                patient_immunizations.occurrenceDateTime[next_dose_idx]
                - vaccination.birthDate
            ).days / 365.25
            if (
                current_dose_age >= 18
                and patient_immunizations.vaccineCode[next_dose_idx]
                in vax_codes["adult_boosters"]
                and (
                    patient_immunizations.occurrenceDateTime[next_dose_idx]
                    - vaccination.occurrenceDateTime
                ).days
                > vax_sequence_specs[initial_vax_type + "_booster_delay"]
            ):
                boosted_date = patient_immunizations.occurrenceDateTime[next_dose_idx]
                break
            elif (
                current_dose_age in range(12, 18)
                and patient_immunizations.vaccineCode[next_dose_idx]
                in vax_codes["pfizer_12to17_boosters"]
                and (
                    patient_immunizations.occurrenceDateTime[next_dose_idx]
                    - vaccination.occurrenceDataTime
                ).days
                > vax_sequence_specs[initial_vax_type + "_booster_delay"]
            ):
                boosted_date = patient_immunizations.occurrenceDateTime[next_dose_idx]
                break

    patient_with_vax_status = patient_immunizations.agg(record_combination_func)
    patient_with_vax_status["vaccinationDate"] = vaccinated_date
    patient_with_vax_status["boosterDate"] = boosted_date
    return patient_with_vax_status


def check_mrna_status(
    idx: int, immunizations: pd.DataFrame, codes: list, second_dose_range: range
) -> datetime.datetime:
    """
    Given a patient's immunization records, a vax code list, and a second dose range,
    determine the date when the patient completed an initial vaccination sequence for
    COVID with an mRNA vaccine.
    """
    vaccinated_date = pd.NaT
    if len(immunizations) > idx + 1:
        days_between_doses = (
            immunizations.occurrenceDateTime[idx + 1]
            - immunizations.occurrenceDateTime[idx]
        ).days
        if (
            immunizations.vaccineCode[idx + 1] in codes
            and days_between_doses in second_dose_range
        ):
            vaccinated_date = immunizations.occurrenceDateTime[
                idx + 1
            ] + datetime.timedelta(days=14)
    return vaccinated_date


if __name__ == "__main__":
    # Set values that specify a blob to load.
    STORAGE_ACCOUNT_URL = "https://pitestdatasa.blob.core.windows.net"
    CONTAINER_NAME = "bronze"
    ELR_FILE_NAME = "CSVS/vxu.csv"
    COVID_VACCINATION_DATAMART_FILENAME = "CSVS/datamarts/covid_vaccine_datamart.csv"

    # Load data.
    print("Loading data...")
    immunizations = pd.read_csv(
        read_blob(STORAGE_ACCOUNT_URL, CONTAINER_NAME, ELR_FILE_NAME)
    )
    covid_vax_codes = pd.read_csv(
        pathlib.Path(__file__).parent / "assets" / "COVID_vaccination_codes.csv"
    )

    # Clean and standardize data.
    print("Data loaded. Cleaning and standardizing...")
    covid_immunizations = pd.merge(
        immunizations, covid_vax_codes, how="inner", on="vaccineCode"
    )
    covid_immunizations.drop(
        columns=[
            "standardizedFirstName",
            "standardizedLastName",
            "standardizedPhone",
            "standardizedAddress",
            "vaccineDescription",
            "vaccine",
        ],
        inplace=True,
    )
    covid_immunizations.birthDate = pd.to_datetime(covid_immunizations.birthDate)
    covid_immunizations.occurrenceDateTime = pd.to_datetime(
        covid_immunizations.occurrenceDateTime
    )
    patients_with_vaccination_status_list = []

    # Review each patient's COVID immunizations and determine their vaccination status.
    print("Data cleaned. Reviewing vaccination records by patient...")
    for hash in tqdm(covid_immunizations.patientHash.unique()):
        patient_immunizations = covid_immunizations.loc[
            covid_immunizations.patientHash == hash
        ].reset_index()
        patient_with_vaccination_status = determine_covid_vax_status(
            patient_immunizations
        )
        patients_with_vaccination_status_list.append(patient_with_vaccination_status)
    covid_vaccination_datamart = pd.concat(
        patients_with_vaccination_status_list, axis=1
    ).T
    covid_vaccination_datamart.drop(
        columns=["vaccineCode", "occurrenceDateTime"], inplace=True
    )

    # Write datamart to blob storage.
    print("Vaccination datamart generated. Writing to blob storage...")
    write_blob(
        covid_vaccination_datamart.to_csv(encoding="utf-8", index=False),
        STORAGE_ACCOUNT_URL,
        CONTAINER_NAME,
        COVID_VACCINATION_DATAMART_FILENAME,
    )
    full_path = (
        STORAGE_ACCOUNT_URL
        + "/"
        + CONTAINER_NAME
        + "/"
        + COVID_VACCINATION_DATAMART_FILENAME
    )
    print(f"Datamart saved to: {full_path}")
