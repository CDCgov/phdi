import warnings

import time
import pandas as pd

from phdi.harmonization import double_metaphone_string
from phdi.linkage import (
    score_linkage_vs_truth,
    feature_match_exact,
    eval_perfect_match,
    perform_linkage_pass,
    compile_match_lists,
    feature_match_fuzzy_string,
    load_json_probs,
    calculate_log_odds,
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
    # Fields that get string comparisons (column in our data set):
    # * First (2)
    # * Last (3)
    # * Address (9)
    # * Email (17)
    # * MRN (18)
    # String comparison LA uses: Levenshtein, variable EM threshold

    # Rule 1:
    # Blocks: first 4 of first and last name, DOB
    # Compare: first, last, street address, MRN, email
    funcs = {
        2: feature_match_fuzzy_string,
        3: feature_match_fuzzy_string,
        9: feature_match_fuzzy_string,
        17: feature_match_fuzzy_string,
        18: feature_match_fuzzy_string,
    }
    print("-------Matching on Rule 1-------")
    matches_1 = perform_linkage_pass(
        data,
        ["FIRST4", "LAST4", "BIRTHDATE"],
        funcs,
        eval_perfect_match,
        cluster_ratio,
        similarity_measure="Levenshtein",
        threshold=0.7,
    )

    # Rule 2:
    # Blocks: first 4 of first and last name, first 4 of address
    # Compare: first, last, street address, MRN, email
    print("-------Matching on Rule 2-------")
    matches_2 = perform_linkage_pass(
        data,
        ["FIRST4", "LAST4", "ADDRESS4"],
        funcs,
        eval_perfect_match,
        cluster_ratio,
        similarity_measure="Levenshtein",
        threshold=0.7,
    )

    # Rule 3:
    # Blocks: DOB
    # Compare: first, last, street address, MRN, email
    print("-------Matching on Rule 3-------")
    matches_3 = perform_linkage_pass(
        data,
        ["BIRTHDATE"],
        funcs,
        eval_perfect_match,
        cluster_ratio,
        similarity_measure="Levenshtein",
        threshold=0.7,
    )

    total_matches = compile_match_lists(
        [matches_1, matches_2, matches_3], cluster_ratio is not None
    )
    return total_matches


def phdi_linkage_algorithm(
    data: pd.DataFrame, cluster_ratio: Union[float, None] = None, **kwargs
) -> dict:
    # Rule 1: metaphone match on first/last, exact on DOB
    # Zip not used, so block on it
    funcs = {
        0: feature_match_fuzzy_string,
        2: feature_match_fuzzy_string,
        3: feature_match_fuzzy_string,
        8: feature_match_exact,
    }
    # print("-------Matching on Rule 1: Metaphone first/last, exact DOB-------")
    matches_1 = perform_linkage_pass(
        data, ["MRN4", "ADDRESS4"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    funcs = {
        16: feature_match_fuzzy_string,
        10: feature_match_fuzzy_string,
    }
    matches_2 = perform_linkage_pass(
        data, ["FIRST4", "LAST4"], funcs, eval_perfect_match, cluster_ratio, **kwargs
    )

    total_matches = compile_match_lists(
        [matches_1, matches_2], cluster_ratio is not None
    )
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


def derive_mrn4(data: pd.DataFrame):
    data["MRN4"] = data["MRN"].apply(lambda x: x[-4:] if len(x) >= 4 else x)
    return data


def add_split_birth_fields(data: pd.DataFrame):
    data["BIRTH_MONTH"] = data["BIRTHDATE"].apply(
        lambda x: x.split("-")[1] if "-" in x else x
    )
    data["BIRTH_YEAR"] = data["BIRTHDATE"].apply(
        lambda x: x.split("-")[0] if "-" in x else x
    )
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
    non_scrambled_misses = missed_df.loc[missed_df["bad_dob"] == "0.0"]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["bad_zip"] == "0.0"]
    non_scrambled_misses = non_scrambled_misses.loc[
        missed_df["bad_name_scramble_first"] == "0.0"
    ]
    non_scrambled_misses = non_scrambled_misses.loc[
        missed_df["bad_name_scramble_last"] == "0.0"
    ]
    non_scrambled_misses = non_scrambled_misses.loc[
        missed_df["bad_name_nickname"] == "0.0"
    ]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["ADDRESS"] == "0"]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["MRN"] == "0"]
    non_scrambled_misses = non_scrambled_misses.loc[missed_df["EMAIL"] == "0"]
    non_scrambled_misses = len(non_scrambled_misses)
    missing_address_misses = len(missed_df.loc[missed_df["ADDRESS"] == "0"])
    missing_mrn_misses = len(missed_df.loc[missed_df["MRN"] == "0"])
    missing_email_misses = len(missed_df.loc[missed_df["EMAIL"] == "0"])
    print("Miss %% on records with scrambled DOB:", scrambled_dobs / len(missed_df))
    print("Miss %% on records with scrambled ZIP:", scrambled_zips / len(missed_df))
    print("Miss %% on records with scrambled FIRST:", scrambled_first / len(missed_df))
    print("Miss %% on records with scrambled LAST:", scrambled_last / len(missed_df))
    print(
        "Miss %% on records with scrambled NICKNAME:",
        scrambled_nickname / float(len(missed_df)),
    )
    print(
        "Miss %% on records with a missing ADDRESS:",
        missing_address_misses / float(len(missed_df)),
    )
    print(
        "Miss %% on records with a missing MRN:",
        missing_mrn_misses / float(len(missed_df)),
    )
    print(
        "Miss %% on records with a missing EMAIL:",
        missing_email_misses / float(len(missed_df)),
    )
    print(
        "Miss %% on records having all fields present without scrambling:",
        non_scrambled_misses / float(len(missed_df)),
    )


data = pd.read_csv(
    "./sample_record_linkage_data_scrambled.csv", dtype="string", nrows=DATA_SIZE
)
data = add_metaphone_columns_to_data(data)
true_matches = determine_true_matches_in_pd_dataset(data)
data = add_split_birth_fields(data)
data = derive_mrn4(data)
data = set_record_id(data)

# start = time.time()
# m_probs = calculate_m_probs(data, true_matches, file_to_write="m_probs_synthetic.json")
# end = time.time()
# print("m-Probabilities took", str(round(end - start, 2)), "seconds to compute.")
# m_probs = load_json_probs("m_probs_synthetic.json")

# start = time.time()
# u_probs = calculate_u_probs(
#     data, true_matches, n_samples=50000, file_to_write="u_probs_synthetic.json"
# )
# end = time.time()
# print("u-Probabilities took", str(round(end - start, 2)), "seconds to compute.")
# u_probs = load_json_probs("u_probs_synthetic.json")

# log_odds = calculate_log_odds(m_probs, u_probs, "log_odds_synthetic.json")
log_odds = load_json_probs("log_odds_synthetic.json")

start = time.time()
# matches = lac_validation_linkage(data, None)
matches = phdi_linkage_algorithm(data, None)
end = time.time()

print("Computation took", str(round(end - start, 2)), "seconds")
display_statistical_evaluation(matches, true_matches)
# display_missed_matches_by_type(matches, true_matches)
