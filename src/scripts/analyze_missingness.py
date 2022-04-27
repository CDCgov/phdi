from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient
from io import StringIO
import pandas as pd
from tabulate import tabulate


def get_blob_data(url: str, container: str, file: str) -> StringIO:
    """
    Use whatever credentials Azure can find to create a blob client and download the
    blob's content as text. In the case where the blob is a CSV the output may be passed
    directly to pandas.read_csv().
    """
    creds = DefaultAzureCredential()
    blob_client = BlobClient(
        account_url=url, container_name=container, blob_name=file, credential=creds
    )
    return StringIO(blob_client.download_blob().content_as_text())


def record_combination_func(x: pd.Series) -> str:
    """
    Aggregation function applied behind the scenes when performing
    de-duplicating linkage. Automatically filters for blank, null,
    and NaN values to facilitate squashing duplicates down into one
    consolidated record, such that, for any column X:
      - if records 1, ..., n-1 are empty in X and record n is not,
        then n(X) is used as a single value
      - if some number of records 1, ..., j <= n have the same value
        in X and all other records are blank in X, then the value
        of the matching columns 1, ..., j is used as a singleton
      - if some number of non-empty in X records 1, ..., j <= n have
        different values in X, then all values 1(X), ..., j(X) are
        concatenated into a list of values delimited by commas
    """
    non_nans = set([x for x in x.astype(str).to_list() if x != ""])
    return ",".join(non_nans)


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
        get_blob_data(STORAGE_ACCOUNT_URL, CONTAINER_NAME, CSV_FULL_NAME)
    )
    pre_linkage.drop(
        columns=[
            c
            for c in pre_linkage.columns
            if c not in list(equity_fields.keys()) + ["patientHash"]
        ],
        inplace=True,
    )
    pre_linkage = filter_for_valid_values(pre_linkage, equity_fields)
    data_by_hash = pre_linkage.groupby("patientHash")
    post_linkage = data_by_hash.agg(record_combination_func).reset_index()
    print("Data loaded and linked.")

    # Compute results and print.
    print("Computing results...")
    patients = count_patients(pre_linkage, post_linkage)
    missing_equity_data = count_records_missing_data(
        pre_linkage, post_linkage, equity_fields
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
