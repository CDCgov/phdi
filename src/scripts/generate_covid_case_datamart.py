import pandas as pd
import pathlib
import json
from typing import List, Callable
from utils import read_blob, record_combination_func, write_blob
from tqdm import tqdm


def standardize_lab_result(result: str, standard: dict) -> str:
    """
    Given a covid test result and dictionary whose keys (POSITIVE, NEGATIVE, and
    INCONCLUSIVE) represent standard results and whose values are lists containing
    non-standard results that map to the associated standard result then return a
    standardized result. Return null if no standard result could not be found.
    """
    try:
        result = result.strip().upper()
    except AttributeError:
        return ""
    for standard_result, non_standard_results in standard.items():
        if result in non_standard_results:
            return standard_result

    return ""


def identify_covid_cases(
    patient_labs: pd.DataFrame, agg_function: Callable
) -> List[pd.Series]:
    """
    Given a data frame containing a single patient's COVID labs and an aggregation
    function, review the labs for possible COVID cases and return a list containing a
    series for each identified case. Data for fields specific to the patient and not the
    infection result from aggregating accross all labs.

    Case Identification Process:
    1.  Check for positive labs:
        a.  If positive labs are found at least one case has been identified.
        b.  The collection date of the earliest positive lab is set as the earliest
            positive specimen collection date for the case.
        c.  Determine case status:
            i.  If there are any positive PCRs in the 90 day period starting on the
                earliest positive specimen collection date then the status is confirmed.
            ii. If there are no positive PCRs in the 90 window this implies that there
                are only positive antigen tests and the case status is probable.
        d. Check for positive labs more than 90 days after the initial positive test.
            i.  If present an additional infection has been identified resulting in
                another case. Repeat steps b-d using the collection date of the first
                lab outside the 90 day window as the new earliest positive specimen
                collection date.
            ii. If not present then all covid cases for the patient have been
                identified.
    2.  If there are no positive labs than the patient has not been infected and no
        cases are identified.

    **** WARNING ****

    As currently written this function applies an approximation of the official CDC/CTSE
    COIVD case defintion. In its current form this function is intended as a proof of
    concept for development purposes.

    Known Limitations:
    1.  Suspect cases resulting from antibody tests are not considered.
    2.  No check has been implemented for a negative PCR within 48 hours of a positive
        Antigen that would negate the case.
    3.  No consideration has been given to how the case definition has changed over the
        course of the pandemic.
    """
    case_list = []
    patient_labs.sort_values(by=["effectiveDateTime"], ascending=True)
    positive_labs = patient_labs.loc[patient_labs.result == "POSITIVE"].reset_index()
    remaining_labs = len(positive_labs)
    while remaining_labs > 0:
        collection_date = positive_labs.effectiveDateTime[0]
        current_infection_labs = positive_labs.loc[
            positive_labs.effectiveDateTime.map(lambda x: (x - collection_date).days)
            <= 90
        ]
        if "pcr" in current_infection_labs.type.to_list():
            status = "confirmed"
        else:
            status = "probable"
        case = patient_labs.agg(record_combination_func)
        case["effectiveDateTime"] = collection_date
        case["status"] = status
        case_list.append(case)
        positive_labs = positive_labs.loc[
            positive_labs.effectiveDateTime.map(lambda x: (x - collection_date).days)
            > 90
        ].reset_index(drop=True)
        remaining_labs = len(positive_labs)
    return case_list


if __name__ == "__main__":

    # Set values that specify a blob to load.
    STORAGE_ACCOUNT_URL = "https://pitestdatasa.blob.core.windows.net"
    CONTAINER_NAME = "bronze"
    ELR_FILE_NAME = "CSVS/elr.csv"
    COVID_CASE_DATAMART_FILENAME = "CSVS/datamarts/covid_case_datamart.csv"

    # Load data.
    print("Loading data...")
    labs = pd.read_csv(read_blob(STORAGE_ACCOUNT_URL, CONTAINER_NAME, ELR_FILE_NAME))
    covid_loincs = pd.read_csv(
        pathlib.Path(__file__).parent / "assets" / "covid_loinc_reference.csv"
    )

    # Clean and standardize data.
    print("Data loaded. Cleaning and standardizing...")
    covid_labs = pd.merge(labs, covid_loincs, how="inner", on="loincCode")
    covid_labs = covid_labs.loc[covid_labs.type.isin(["pcr", "ag"])]
    covid_labs.drop(columns=["loincCode", "notes"], inplace=True)
    standard_results = json.loads(
        open(
            pathlib.Path(__file__).parent / "assets" / "covid_lab_results_standard.json"
        ).read()
    )
    covid_labs.result = covid_labs.result.map(
        lambda x: (standardize_lab_result(x, standard_results))
    )
    covid_labs.effectiveDateTime = pd.to_datetime(covid_labs.effectiveDateTime)

    # Find COVID cases and generate datamart.
    print("Data cleaned. Reviewing lab records by patient...")
    case_list = []
    for hash in tqdm(covid_labs.patientHash.unique()):
        patient_labs = covid_labs.loc[covid_labs.patientHash == hash]
        cases = identify_covid_cases(patient_labs, record_combination_func)
        case_list.extend(cases)

    covid_case_datamart = pd.concat(case_list, axis=1).T
    covid_case_datamart.drop(columns=["result", "type"], inplace=True)

    # Write datamart to blob storage.
    print("COVID case datamart generated. Writing to blob storage...")
    write_blob(
        covid_case_datamart.to_csv(encoding="utf-8", index=False),
        STORAGE_ACCOUNT_URL,
        CONTAINER_NAME,
        COVID_CASE_DATAMART_FILENAME,
    )
    full_path = (
        STORAGE_ACCOUNT_URL + "/" + CONTAINER_NAME + "/" + COVID_CASE_DATAMART_FILENAME
    )
    print(f"Datamart saved to: {full_path}")
