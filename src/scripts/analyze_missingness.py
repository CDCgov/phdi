import pandas as pd
import pathlib
from tabulate import tabulate
from utils import read_blob, record_combination_func


def filter_for_valid_values(df: pd.DataFrame, values_by_column: dict[str, set[str]]):
    """
    Given a dataframe and a dictionary mapping columns to allowed values,
    filter the df such that the provided columns contain only values
    that are pre-defined as valid.
    """
    for col in values_by_column:
        df[col] = df[col].map(lambda x: x if x in values_by_column[col] else "")
    return df


def count_patients(pre_linkage: pd.DataFrame, post_linkage: pd.DataFrame) -> dict:
    """
    Given a data frames with records before and after linkage return a dictionary
    containing the number of distinct patients in each as well as the percent reduction.
    """
    patient_results = {}
    patient_results["pre-linkage"] = len(pre_linkage)
    patient_results["post-linkage"] = len(post_linkage)
    patient_results["percent-reduction"] = round(
        (
            (patient_results["pre-linkage"] - patient_results["post-linkage"])
            / patient_results["pre-linkage"]
        )
        * 100,
        0,
    )
    return patient_results


def count_records_missing_data(
    pre_linkage: pd.DataFrame, post_linkage: pd.DataFrame, columns_and_values: dict
) -> dict:
    """
    Given datasets pre and post linkage as well as a dictionary whose keys specify
    columns of interests and values are sets of acceptable values for the corresponding
    columns return a dictionary reporting the number of records missing data in each of
    the columns of interest.
    """
    results = {
        "field": [],
        "pre-linkage-count": [],
        "pre-linkage-percent": [],
        "post-linkage-count": [],
        "post-linkage-percent": [],
    }
    for idx, column in enumerate(columns_and_values):
        results["field"].append(column)
        results["pre-linkage-count"].append(
            len(pre_linkage.loc[~pre_linkage[column].isin(columns_and_values[column])])
        )
        results["pre-linkage-percent"].append(
            round((results["pre-linkage-count"][idx] / len(pre_linkage)) * 100, 1)
        )
        results["post-linkage-count"].append(
            len(post_linkage.loc[post_linkage[column].apply(len) == 0])
        )
        results["post-linkage-percent"].append(
            round((results["post-linkage-count"][idx] / len(post_linkage)) * 100, 1)
        )
    return results


if __name__ == "__main__":

    # Set values the specify a blob to load.
    STORAGE_ACCOUNT_URL = "https://pitestdatasa.blob.core.windows.net"
    CONTAINER_NAME = "bronze"
    CSV_FULL_NAME = "csv-test/elr.csv"

    # Define sets of known affirmative values for gender, race, and ethnicity.
    genders = {"male", "female"}
    races = {"1002-5", "2028-9", "2054-5", "2076-8", "2131-1", "2106-3", "W"}
    ethnicities = {"2135-2", "2186-5"}
    equity_fields = {"gender": genders, "race": races, "ethnicity": ethnicities}

    # Load data and link patient records.
    print("Loading data...")
    pre_linkage = pd.read_csv(
        read_blob(STORAGE_ACCOUNT_URL, CONTAINER_NAME, CSV_FULL_NAME)
    )

    # Use known COVID LOINC codes to filter out all rows corresponding to observation
    # resources reporting anything other than covid test results (e.g. observations
    # corresponding to AOEs)
    covid_loincs = pd.read_csv(
        pathlib.Path(__file__).parent / "assets" / "covid_loinc_reference.csv"
    )

    pre_linkage_covid = pre_linkage.merge(covid_loincs, on="loincCode", how="inner")

    pre_linkage_covid.drop(
        columns=[
            c
            for c in pre_linkage_covid.columns
            if c not in list(equity_fields.keys()) + ["patientHash"]
        ],
        inplace=True,
    )
    pre_linkage_covid = filter_for_valid_values(pre_linkage_covid, equity_fields)
    data_by_hash = pre_linkage_covid.groupby("patientHash")
    post_linkage_covid = data_by_hash.agg(record_combination_func).reset_index()
    print("Data loaded and linked.")

    # Compute results and print.
    print("Computing results...")
    patients = count_patients(pre_linkage_covid, post_linkage_covid)
    missing_equity_data = count_records_missing_data(
        pre_linkage_covid, post_linkage_covid, equity_fields
    )
    print("Results computed.")
    print("\nNumber of patient records as a function of linkage:")
    print("\n" + tabulate(patients.items(), headers=["#", "patients"]) + "\n")
    print(
        "Number of records missing fields key for PH Equity as a functions of linkage:"
    )
    print(
        "\n" + tabulate(missing_equity_data, headers=missing_equity_data.keys()) + "\n"
    )
