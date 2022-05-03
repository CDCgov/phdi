import pandas as pd
import pathlib
from tabulate import tabulate
from utils import record_combination_func


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


def find_one_patient_per_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    ECR and VXU data sets, as they've been given to us, contain a
    patient's entire case or vaccination history, respectively. This
    means when we convert to FHIR, all individual observations are split
    into separate messages, which the CSV generator parses as separate
    rows. The effect is that one patient could appear multiple times
    in a CSV for covid-related reasons, even if in the data they formed
    a single concrete unit. This function is a quick and dirty hack
    to work around this by preserving only the first instance of a
    patient's hash in the data set. It is useful PURELY for determining
    how many records our hash actually linked.
    """
    prev_hash = None
    idxs_to_keep = []
    for row in df.index:
        if prev_hash is None or df["patientHash"][row] != prev_hash:
            idxs_to_keep.append(row)
            prev_hash = df["patientHash"][row]
    new_df = df.loc[idxs_to_keep, :]
    new_df.reset_index(drop=True)
    return new_df


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
    pre_linkage_elr = pd.read_csv("../FunctionApps/python/elr.csv", dtype="object")
    pre_linkage_ecr = pd.read_csv("../FunctionApps/python/ecr.csv", dtype="object")
    pre_linkage_vxu = pd.read_csv("../FunctionApps/python/vxu.csv", dtype="object")
    pre_linkage_ecr.rename(columns={"observationLoincCode": "loincCode"}, inplace=True)
    pre_linkage_ecr.rename(
        columns={"immunizationVaccineCode": "vaccineCode"}, inplace=True
    )
    pre_linkage_vxu.rename(
        columns={"immunizationVaccineCode": "vaccineCode"}, inplace=True
    )

    # Use known COVID LOINC codes to filter out all rows corresponding to observation
    # resources reporting anything other than covid test results (e.g. observations
    # corresponding to AOEs)
    covid_loincs = pd.read_csv(
        pathlib.Path(__file__).parent / "assets" / "covid_loinc_reference.csv"
    )
    # Use known COVID vaccine related codes as described in
    # https://build.fhir.org/ig/HL7/fhir-COVID19Library-ig/branches/master/ValueSet-covid19-cvx-codes-value-set.html
    # to filter out any non-covid vaccines
    covid_vax_codes = pd.read_csv(
        pathlib.Path(__file__).parent / "assets" / "covid_vax_codes.csv", dtype="object"
    )

    pre_linkage_elr = pre_linkage_elr.merge(covid_loincs, on="loincCode", how="inner")
    pre_linkage_ecr = pre_linkage_ecr.merge(covid_loincs, on="loincCode", how="inner")
    pre_linkage_ecr = find_one_patient_per_report(pre_linkage_ecr)
    pre_linkage_vxu = pre_linkage_vxu.merge(
        covid_vax_codes, on="vaccineCode", how="inner"
    )
    pre_linkage_vxu = find_one_patient_per_report(pre_linkage_vxu)
    for dtype in [pre_linkage_elr, pre_linkage_ecr, pre_linkage_vxu]:
        dtype.drop(
            columns=[
                c
                for c in dtype.columns
                if c not in list(equity_fields.keys()) + ["patientHash"]
            ],
            inplace=True,
        )
    pre_linkage_covid = pd.concat(
        [pre_linkage_elr, pre_linkage_ecr, pre_linkage_vxu], ignore_index=True
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
    print("\nNumber of patient records before and after record linkage:")
    print("\n" + tabulate(patients.items(), headers=["#", "patients"]) + "\n")
    print("Number of records missing a PH equity field, before and after linkage:")
    print(
        "\n" + tabulate(missing_equity_data, headers=missing_equity_data.keys()) + "\n"
    )
