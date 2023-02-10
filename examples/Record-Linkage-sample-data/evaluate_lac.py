import warnings

import pandas as pd

from phdi.harmonization import double_metaphone_string
from phdi.linkage import (
    score_linkage_vs_truth,
    feature_match_exact,
    eval_perfect_match,
    perform_linkage_pass,
    compile_match_lists,
    feature_match_four_char,
)
from typing import Union

DATA_SIZE = 50000
warnings.simplefilter(action="ignore", category=FutureWarning)


def lac_validation_linkage(
    data: pd.DataFrame, cluster_ratio: Union[float, None] = None, **kwargs
) -> dict:
    """
    Perform a simplified run of the linkage algorithm currently used by LAC.
    This algorithm is purely deterministic and uses three rules:

      1. exact match on first 4 characters of each of first and last name,
        and exact match on full DOB
      2. exact match on first 4 characters of first and last name, and
        exact match on first 4 chars of zip code
      3. exact match on full DOB

    No expectation maximization is used in this algorithm to estimate
    initial match weights, since true matches are assumed to be known in
    advance via synthetic data generation.

    :param data: The pandas dataframe of records to link.
    :param cluster_ratio: An optional parameter indicating whether to run
      the algorithm in clustering mode. Default is false.
    :return: A dictionary holding all found matches during each pass of
      the algorithm.
    """

    # Rule 1: exact match on first 4 of first, first 4 of last, DOB
    # Zip not used, so block on it
    funcs = {
        0: feature_match_exact,
        1: feature_match_four_char,
        2: feature_match_four_char,
    }
    print("-------Matching on Rule 1: First 4 of First/Last, Exact DOB-------")
    matches_1 = perform_linkage_pass(
        data, ["ZIP"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    # Rule 2: exact match on first 4 of first, first 4 of last,
    # first 4 of zip--DOB not used, so block on it
    funcs = {
        1: feature_match_four_char,
        2: feature_match_four_char,
        13: feature_match_four_char,
    }
    print("-------Matching on Rule 2: First 4 of First/Last/Zip-------")
    matches_2 = perform_linkage_pass(
        data, ["BIRTHDATE"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    # Rule 3: exact match just on full DOB
    # Zip not used, block on it
    funcs = {0: feature_match_exact}
    print("-------Matching on Rule 3: Exact DOB-------")
    matches_3 = perform_linkage_pass(
        data, ["ZIP"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    total_matches = compile_match_lists(
        [matches_1, matches_2, matches_3], cluster_ratio is not None
    )
    return total_matches


def phdi_linkage_algorithm(
    data: pd.DataFrame, cluster_ratio: Union[float, None] = None, **kwargs
) -> dict:
    # Rule 1: exact match on first/last/DOB
    # Zip not used, so block on it
    # funcs = {
    #     0: feature_match_exact,
    #     1: feature_match_exact,
    #     2: feature_match_exact,
    # }
    # print("-------Matching on Rule 1: Exact First/Last/DOB-------")
    # matches_1 = perform_linkage_pass(
    #     data, ["ZIP"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    # )

    # Rule 2: fuzzy match on first/last, exact match on sex,
    # exact match on zip--DOB not used, so block on it
    funcs = {
        0: feature_match_exact,
        23: feature_match_exact,
        24: feature_match_exact,
    }
    print("-------Matching on Rule 2: Metaphone first/last, exact DOB-------")
    matches_2 = perform_linkage_pass(
        data, ["ZIP"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    # Rule 3: exact match on sex/zip, fuzzy match on DOB
    # City not used, block on it
    # funcs = {
    #     0: feature_match_fuzzy_string,
    #     3: feature_match_exact,
    #     7: feature_match_exact,
    # }
    # print("-------Matching on Rule 3: Fuzzy First/Last, Exact Zip, Fuzzy DOB-------")
    # matches_3 = perform_linkage_pass(
    #     data, ["GENDER"], funcs, eval_perfect_match, cluster_ratio, threshold=0.9
    # )

    total_matches = compile_match_lists([matches_2], cluster_ratio is not None)
    return total_matches


def determine_true_matches_in_pd_dataset(data: pd.DataFrame):
    print("-------Identifying True Matches for Evaluation-------")
    true_matches = {}
    tuple_data = tuple(data.groupby("Id"))
    for _, sub_df in tuple_data:
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
data = data.loc[:DATA_SIZE]
data = add_metaphone_columns_to_data(data)
true_matches = determine_true_matches_in_pd_dataset(data)
data = set_record_id(data)
# matches = lac_validation_linkage(data, None)
matches = phdi_linkage_algorithm(data, None)
display_statistical_evaluation(matches, true_matches)
# display_missed_matches_by_type(matches, true_matches)
