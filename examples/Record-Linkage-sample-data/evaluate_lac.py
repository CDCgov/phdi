import warnings

import pandas as pd

from phdi.harmonization import double_metaphone_string
from phdi.linkage import lac_validation_linkage, score_linkage_vs_truth
from phdi.linkage.link import phdi_linkage_algorithm
from typing import Union

DATA_SIZE = 50000
warnings.simplefilter(action="ignore", category=FutureWarning)


def determine_true_matches_in_pd_dataset(data: pd.DataFrame):
    print("-------Identifying True Matches for Evaluation-------")
    true_matches = {}
    tuple_data = tuple(data.groupby("Id"))
    for master_patient, sub_df in tuple_data:
        sorted_idx = sorted(sub_df.index)
        for idx in range(len(sorted_idx)):
            r_idx = sorted_idx[idx]
            if r_idx not in true_matches:
                true_matches[r_idx] = set()
            for i in range(idx + 1, len(sorted_idx)):
                true_matches[r_idx].add(sorted_idx[i])
    return true_matches


def set_record_id(data: pd.DataFrame):
    data["ID"] = data.index
    data = data.drop(columns=["Id"])
    return data


def add_metaphone_columns_to_data(data: pd.DataFrame):
    data["DM_FIRST"] = data["FIRST"].apply(lambda x: double_metaphone_string(x)[0])
    data["DM_LAST"] = data["LAST"].apply(lambda x: double_metaphone_string(x)[0])
    return data


def identify_missed_matches(
    found_matches: dict[Union[int, str], set],
    true_matches: dict[Union[int, str], set],
):
    missed_matches = {}
    for root_record in true_matches:
        if root_record in found_matches:
            diffset = true_matches[root_record].difference(found_matches[root_record])
            if len(diffset) > 0:
                missed_matches[root_record] = diffset
        elif len(true_matches[root_record]) > 0:
            missed_matches[root_record] = true_matches[root_record]
    return missed_matches


def get_indices_affected_by_misses(missed_matches: dict):
    affected_records = set()
    for record in missed_matches:
        affected_records.add(record)
        affected_records.update(missed_matches[record])
    affected_records = sorted(list(affected_records))
    return affected_records


def display_statistical_evaluation(matches: dict, true_matches: dict):
    sensitivitiy, specificity, ppv, f1 = score_linkage_vs_truth(
        matches, true_matches, DATA_SIZE
    )
    print("Sensitivity:", sensitivitiy)
    print("Specificity:", specificity)
    print("PPV:", ppv)
    print("F1:", f1)


def display_missed_matches_by_type(matches: dict, true_matches: dict):
    missed_matches = identify_missed_matches(matches, true_matches)
    affected_indices = get_indices_affected_by_misses(missed_matches)
    missed_df = data.iloc[affected_indices]
    scrambled_dobs = missed_df["bad_dob"].astype(float).sum()
    scrambled_zips = missed_df["bad_zip"].astype(float).sum()
    scrambled_first = missed_df["bad_name_scramble_first"].astype(float).sum()
    scrambled_last = missed_df["bad_name_scramble_last"].astype(float).sum()
    scrambled_nickname = missed_df["bad_name_nickname"].astype(float).sum()
    non_scrambled_misses = missed_df.loc[missed_df["bad_dob"] == 0]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["bad_zip"] == 0]
    non_scrambled_misses = non_scrambled_misses.loc[
        missed_df["bad_name_scramble_first"] == 0
    ]
    non_scrambled_misses = non_scrambled_misses.loc[
        missed_df["bad_name_scramble_last"] == 0
    ]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["bad_name_nickname"] == 0]
    non_scrambled_misses = len(non_scrambled_misses)
    missing_address_misses = len(missed_df.loc[missed_df["ADDRESS"] == 0])
    print("Misses on records with scrambled DOB:", scrambled_dobs / len(missed_df))
    print("Misses on records with scrambled ZIP:", scrambled_zips / len(missed_df))
    print("Misses on records with scrambled FIRST:", scrambled_first / len(missed_df))
    print("Misses on records with scrambled LAST:", scrambled_last / len(missed_df))
    print(
        "Misses on records with scrambled NICKNAME:",
        scrambled_nickname / len(missed_df),
    )
    print(
        "Misses on records with a missing ADDRESS:",
        missing_address_misses / len(missed_df),
    )
    print(
        "Misses on records with no scrambling:", non_scrambled_misses / len(missed_df)
    )


data = pd.read_csv("./sample_record_linkage_data_scrambled.csv", dtype="string")
# cols_to_keep = [
#     "Id",
#     "BIRTHDATE",
#     "FIRST",
#     "LAST",
#     "GENDER",
#     "ADDRESS",
#     "CITY",
#     "STATE",
#     "ZIP",
# ]
data = data.loc[:DATA_SIZE]
data = add_metaphone_columns_to_data(data)
# data = data.drop(columns=[c for c in data.columns if c not in cols_to_keep])
true_matches = determine_true_matches_in_pd_dataset(data)
data = set_record_id(data)
# matches = lac_validation_linkage(data, None)
matches = phdi_linkage_algorithm(data, None)
display_statistical_evaluation(matches, true_matches)
# display_missed_matches_by_type(matches, true_matches)
