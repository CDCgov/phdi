import json
import os
import pandas as pd
import random

from phdi.linkage import (
    generate_hash_str,
    block_data,
    feature_match_exact,
    feature_match_fuzzy_string,
    eval_perfect_match,
    match_within_block,
    compile_match_lists,
    feature_match_four_char,
    perform_linkage_pass,
    score_linkage_vs_truth,
    block_data_from_db,
    _generate_block_query,
    calculate_m_probs,
    calculate_u_probs,
    calculate_log_odds,
    load_json_probs,
    eval_log_odds_cutoff,
    feature_match_log_odds_exact,
    feature_match_log_odds_fuzzy_compare,
    extract_blocking_values_from_record,
    write_linkage_config,
    read_linkage_config,
)
from phdi.linkage.link import (
    _match_within_block_cluster_ratio,
    _map_matches_to_record_ids,
)

import pathlib
import pytest
from random import seed
from math import log
from json.decoder import JSONDecodeError


def test_extract_blocking_values_from_record():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    patient = [
        r.get("resource")
        for r in bundle.get("entry")
        if r.get("resource", {}).get("resourceType") == "Patient"
    ][0]
    patient["name"][0]["family"] = "Shepard"

    with pytest.raises(ValueError) as e:
        extract_blocking_values_from_record(patient, {"invalid"}, {})
    assert "is not a supported extraction field" in str(e.value)

    with pytest.raises(ValueError) as e:
        extract_blocking_values_from_record(
            patient, {"first_name"}, {"first_name": "invalid_transform"}
        )
    assert "Transformation invalid_transform is not valid" in str(e.value)

    blocking_fields = [
        "first_name",
        "last_name",
        "zip",
        "city",
        "birthdate",
        "sex",
        "state",
        "address",
    ]
    transforms = {"first_name": "first4", "last_name": "first4", "address": "last4"}
    blocking_vals = extract_blocking_values_from_record(
        patient, blocking_fields, transforms
    )
    assert blocking_vals == {
        "first_name": "John",
        "last_name": "Shep",
        "zip": "10001-0001",
        "city": "Faketon",
        "birthdate": "1983-02-01",
        "sex": "female",
        "state": "NY",
        "address": "e St",
    }


def test_generate_hash():
    salt_str = "super-legit-salt"
    patient_1 = "John-Shepard-2153/11/07-1234 Silversun Strip Zakera Ward Citadel 99999"
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"

    hash_1 = generate_hash_str(patient_1, salt_str)
    hash_2 = generate_hash_str(patient_2, salt_str)

    assert hash_1 == "0aa5aa1f6183a24670b2e1848864514e119ae6ca63bb35246ef215e7a0746a35"
    assert hash_2 == "102818c623290c24069beb721c6eb465d281b3b67ecfb6aef924d14affa117b9"


def test_feature_match_exact():
    record_i = [1, 0, -1, "blah", "", True]
    record_j = [1, 0, -1, "blah", "", True]
    record_k = [2, 10, -10, "no match", "null", False]

    # Simultaneously test matches and non-matches of different data types
    for i in range(len(record_i)):
        assert feature_match_exact(record_i, record_j, i)
        assert not feature_match_exact(record_i, record_k, i)

    # Special case for matching None--None == None is vacuous
    assert feature_match_exact([None], [None], 0)


def test_feature_match_fuzzy_string():
    record_i = ["string1", "John", "John", "", None]
    record_j = ["string2", "Jhon", "Jon", "", None]
    for i in range(len(record_i)):
        assert feature_match_fuzzy_string(
            record_i,
            record_j,
            i,
            similarity_measure="JaroWinkler",
            threshold=0.7,
        )
    assert not feature_match_fuzzy_string(
        ["no match"],
        ["dont match me bro"],
        0,
        similarity_measure="JaroWinkler",
        threshold=0.7,
    )


def test_eval_perfect_match():
    assert eval_perfect_match([1, 1, 1])
    assert not eval_perfect_match([1, 1, 0])
    assert not eval_perfect_match([1, 0, 0])
    assert not eval_perfect_match([0, 0, 0])


def test_match_within_block_cluster_ratio():
    data = [
        [1, "John", "Shepard", "11-7-2153", "90909"],
        [5, "Jhon", "Sheperd", "11-7-2153", "90909"],
        [11, "Jon", "Shepherd", "11-7-2153", "90909"],
        [12, "Johnathan", "Shepard", "11-7-2153", "90909"],
        [13, "Nathan", "Shepard", "11-7-2153", "90909"],
        [14, "Jane", "Smith", "01-10-1986", "12345"],
        [18, "Daphne", "Walker", "12-12-1992", "23456"],
        [23, "Alejandro", "Villanueve", "1-1-1980", "15935"],
        [24, "Alejandro", "Villanueva", "1-1-1980", "15935"],
        [27, "Philip", "", "2-2-1990", "64873"],
        [31, "Alejandr", "Villanueve", "1-1-1980", "15935"],
        [32, "Aelxdrano", "Villanueve", "1-1-1980", "15935"],
    ]

    eval_rule = eval_perfect_match
    funcs = {
        1: feature_match_fuzzy_string,
        2: feature_match_fuzzy_string,
        3: feature_match_exact,
        4: feature_match_exact,
    }

    # Do a test run requiring total membership match
    matches = _match_within_block_cluster_ratio(
        data, 1.0, funcs, eval_rule, threshold=0.8
    )
    assert matches == [{0, 1, 2}, {3}, {4}, {5}, {6}, {7, 8, 10}, {9}, {11}]

    # Now do a test showing different cluster groupings
    matches = _match_within_block_cluster_ratio(
        data, 0.6, funcs, eval_rule, threshold=0.8
    )
    assert matches == [{0, 1, 2, 3}, {4}, {5}, {6}, {7, 8, 10, 11}, {9}]


def test_match_within_block():
    # Data will be of the form:
    # patient_id, first_name, last_name, DOB, zip code
    data = [
        [1, "John", "Shepard", "11-7-2153", "90909"],
        [5, "Jhon", "Sheperd", "11-7-2153", "90909"],
        [11, "Jon", "Shepherd", "11-7-2153", "90909"],
        [14, "Jane", "Smith", "01-10-1986", "12345"],
        [18, "Daphne", "Walker", "12-12-1992", "23456"],
        [23, "Alejandro", "Villanueve", "1-1-1980", "15935"],
        [24, "Alejandro", "Villanueva", "1-1-1980", "15935"],
        [27, "Philip", "", "2-2-1990", "64873"],
        [31, "Alejandr", "Villanueve", "1-1-1980", "15935"],
    ]
    eval_rule = eval_perfect_match

    # First, require exact matches on everything to match
    # Expect 0 pairs
    funcs = {
        1: feature_match_exact,
        2: feature_match_exact,
        3: feature_match_exact,
        4: feature_match_exact,
    }
    match_pairs = match_within_block(data, funcs, eval_rule)
    assert len(match_pairs) == 0

    # Now, require exact on DOB and zip, but allow fuzzy on first and last
    # Expect 6 matches
    funcs[1] = feature_match_fuzzy_string
    funcs[2] = feature_match_fuzzy_string
    match_pairs = match_within_block(data, funcs, eval_rule)
    assert match_pairs == [(0, 1), (0, 2), (1, 2), (5, 6), (5, 8), (6, 8)]

    # As above, but let's be explicit about string comparison and threshold
    # Expect three matches, but none with the "Johns"
    # Note the difference in returned results by changing distance function
    match_pairs = match_within_block(
        data, funcs, eval_rule, similarity_measure="Levenshtein", threshold=0.8
    )
    assert match_pairs == [(5, 6), (5, 8), (6, 8)]


def test_block_parquet_data():
    # Create data for testing
    test_data = {
        "id": [0, 1, 2, 3],
        "first_name": ["Marc", "Mark", "Jose", "Eliza"],
        "last_name": ["Gutierrez", "Smith", "Garcia", "Jones"],
        "zip": [90210, 90210, 90210, 90006],
        "year_of_birth": [1980, 1992, 1992, 1992],
    }
    test_data_df = pd.DataFrame.from_dict(test_data)

    if os.path.isfile("./test.parquet"):  # pragma: no cover
        os.remove("./test.parquet")
    test_data_df.to_parquet(path="./test.parquet", engine="pyarrow")

    test_data = pd.read_parquet(path="./test.parquet", engine="pyarrow")
    blocked_test_data = block_data(test_data, blocks=["zip"])

    # Test output data types are correct
    assert isinstance(blocked_test_data, dict)
    assert isinstance(blocked_test_data[90006], list)

    # Test that the number of blocks is the same as the distinct number of zip codes
    assert len(blocked_test_data.keys()) == test_data_df["zip"].nunique()

    # Test blocks with multiple block columns
    blocked_test_data = block_data(test_data, blocks=["zip", "year_of_birth"])
    assert len(blocked_test_data[(90210, 1992)]) == 2

    # Clean up
    if os.path.isfile("./test.parquet"):  # pragma: no cover
        os.remove("./test.parquet")


def test_compile_match_lists():
    data = [
        ["11-7-2153", "John", "Shepard", "", "", "", "", "90909", 1],
        ["11-7-2153", "Jhon", "Sheperd", "", "", "", "", "90909", 5],
        ["11-7-2153", "Jon", "Shepherd", "", "", "", "", "90909", 11],
        ["11-7-2153", "Johnathan", "Shepard", "", "", "", "", "90909", 12],
        ["11-7-2153", "Nathan", "Shepard", "", "", "", "", "90909", 13],
        ["01-10-1986", "Jane", "Smith", "", "", "", "", "12345", 14],
        ["12-12-1992", "Daphne", "Walker", "", "", "", "", "23456", 18],
        ["1-1-1980", "Alejandro", "Villanueve", "", "", "", "", "15935", 23],
        ["1-1-1980", "Alejandro", "Villanueva", "", "", "", "", "15935", 24],
        ["2-2-1990", "Philip", "", "", "", "", "", "64873", 27],
        ["1-1-1980", "Alejandr", "Villanueve", "", "", "", "", "15935", 31],
        ["1-1-1980", "Aelxdrano", "Villanueve", "", "", "", "", "15935", 32],
    ]
    data = pd.DataFrame(
        data,
        columns=[
            "BIRTHDATE",
            "FIRST",
            "LAST",
            "GENDER",
            "ADDRESS",
            "CITY",
            "STATE",
            "ZIP",
            "ID",
        ],
    )
    funcs = {
        1: feature_match_four_char,
        2: feature_match_four_char,
        3: feature_match_exact,
    }
    matches_1 = perform_linkage_pass(data, ["ZIP"], funcs, eval_perfect_match)
    funcs = {
        1: feature_match_four_char,
        2: feature_match_four_char,
        4: feature_match_four_char,
    }
    matches_2 = perform_linkage_pass(data, ["BIRTHDATE"], funcs, eval_perfect_match)
    funcs = {3: feature_match_exact}
    matches_3 = perform_linkage_pass(data, ["ZIP"], funcs, eval_perfect_match)
    assert compile_match_lists([matches_1, matches_2, matches_3], False) == {
        1: {5, 11, 12, 13},
        5: {11, 12, 13},
        11: {12, 13},
        12: {13},
        23: {24, 31, 32},
        24: {31, 32},
        31: {32},
    }


def test_feature_match_four_char():
    record_i = ["Johnathan", "Shepard"]
    record_j = ["John", "Sheperd"]
    record_k = ["Jhon", "Sehpard"]

    # Simultaneously test matches and non-matches of different data types
    for i in range(len(record_i)):
        assert feature_match_four_char(record_i, record_j, i)
        assert not feature_match_four_char(record_i, record_k, i)


def test_map_matches_to_ids():
    data = [
        ["11-7-2153", "John", "Shepard", "", "", "", "", "90909", 1],
        ["11-7-2153", "Jhon", "Sheperd", "", "", "", "", "90909", 5],
        ["11-7-2153", "Jon", "Shepherd", "", "", "", "", "90909", 11],
        ["11-7-2153", "Johnathan", "Shepard", "", "", "", "", "90909", 12],
        ["11-7-2153", "Nathan", "Shepard", "", "", "", "", "90909", 13],
        ["01-10-1986", "Jane", "Smith", "", "", "", "", "12345", 14],
        ["12-12-1992", "Daphne", "Walker", "", "", "", "", "23456", 18],
        ["1-1-1980", "Alejandro", "Villanueve", "", "", "", "", "15935", 23],
        ["1-1-1980", "Alejandro", "Villanueva", "", "", "", "", "15935", 24],
        ["2-2-1990", "Philip", "", "", "", "", "", "64873", 27],
        ["1-1-1980", "Alejandr", "Villanueve", "", "", "", "", "15935", 31],
        ["1-1-1980", "Aelxdrano", "Villanueve", "", "", "", "", "15935", 32],
    ]
    data = pd.DataFrame(
        data,
        columns=[
            "BIRTHDATE",
            "FIRST",
            "LAST",
            "GENDER",
            "ADDRESS",
            "CITY",
            "STATE",
            "ZIP",
            "ID",
        ],
    )
    blocked_data = block_data(data, ["ZIP"])
    matches_with_ids = {
        "12345": [],
        "15935": [(23, 24), (23, 31), (24, 31)],
        "23456": [],
        "64873": [],
        "90909": [(1, 12)],
    }
    found_matches = {
        "12345": [],
        "15935": [(0, 1), (0, 2), (1, 2)],
        "23456": [],
        "64873": [],
        "90909": [(0, 3)],
    }
    for block in matches_with_ids:
        assert matches_with_ids[block] == _map_matches_to_record_ids(
            found_matches[block], blocked_data[block]
        )

    # Now test in cluster mode
    found_matches = {
        "12345": set(),
        "15935": {0, 1, 2},
        "23456": set(),
        "64873": set(),
        "90909": {0, 3},
    }


def test_perform_linkage_pass():
    data = [
        ["11-7-2153", "John", "Shepard", "", "", "", "", "90909", 1],
        ["11-7-2153", "Jhon", "Sheperd", "", "", "", "", "90909", 5],
        ["11-7-2153", "Jon", "Shepherd", "", "", "", "", "90909", 11],
        ["11-7-2153", "Johnathan", "Shepard", "", "", "", "", "90909", 12],
        ["11-7-2153", "Nathan", "Shepard", "", "", "", "", "90909", 13],
        ["01-10-1986", "Jane", "Smith", "", "", "", "", "12345", 14],
        ["12-12-1992", "Daphne", "Walker", "", "", "", "", "23456", 18],
        ["1-1-1980", "Alejandro", "Villanueve", "", "", "", "", "15935", 23],
        ["1-1-1980", "Alejandro", "Villanueva", "", "", "", "", "15935", 24],
        ["2-2-1990", "Philip", "", "", "", "", "", "64873", 27],
        ["1-1-1980", "Alejandr", "Villanueve", "", "", "", "", "15935", 31],
        ["1-1-1980", "Aelxdrano", "Villanueve", "", "", "", "", "15935", 32],
    ]
    data = pd.DataFrame(
        data,
        columns=[
            "BIRTHDATE",
            "FIRST",
            "LAST",
            "GENDER",
            "ADDRESS",
            "CITY",
            "STATE",
            "ZIP",
            "ID",
        ],
    )
    funcs = {
        1: feature_match_four_char,
        2: feature_match_four_char,
        3: feature_match_exact,
    }
    matches = perform_linkage_pass(data, ["ZIP"], funcs, eval_perfect_match, None)
    assert matches == {
        "12345": [],
        "15935": [(23, 24), (23, 31), (24, 31)],
        "23456": [],
        "64873": [],
        "90909": [(1, 12)],
    }

    # Now test again in cluster mode
    matches = perform_linkage_pass(
        data, ["ZIP"], funcs, eval_perfect_match, cluster_ratio=0.75
    )
    assert matches == {
        "12345": [{14}],
        "15935": [{24, 31, 23}, {32}],
        "23456": [{18}],
        "64873": [{27}],
        "90909": [{1, 12}, {5}, {11}, {13}],
    }


def test_score_linkage_vs_truth():
    num_records = 12
    matches = {
        1: {5, 11, 12, 13},
        5: {11, 12, 13},
        11: {12, 13},
        12: {13},
        23: {24, 31, 32},
        24: {31, 32},
        31: {32},
    }
    true_matches = {
        1: {5, 11, 12},
        5: {11, 12},
        11: {12},
        23: {24, 31, 32},
        24: {31, 32},
        31: {32},
    }
    sensitivity, specificity, ppv, f1 = score_linkage_vs_truth(
        matches, true_matches, num_records
    )
    assert sensitivity == 1.0
    assert specificity == 0.926
    assert ppv == 0.75
    assert f1 == 0.857

    cluster_mode_matches = {1: {5, 11, 12, 13}, 23: {24, 31, 32}}
    sensitivity, specificity, ppv, f1 = score_linkage_vs_truth(
        cluster_mode_matches, true_matches, num_records, True
    )
    assert sensitivity == 1.0
    assert specificity == 0.926
    assert ppv == 0.75
    assert f1 == 0.857


def test_generate_block_query():
    table_name = "test_table"
    block_data = {"ZIP": 90210, "City": "Los Angeles"}
    correct_query = (
        f"SELECT * FROM {table_name} WHERE "
        + f"{list(block_data.keys())[0]} = {list(block_data.values())[0]} "
        + f"AND {list(block_data.keys())[1]} = '{list(block_data.values())[1]}'"
    )

    query = _generate_block_query(table_name, block_data)

    assert query == correct_query

    # Tests for appropriate data type handling in query generation
    assert (
        type(list(block_data.values())[1]) == str
        and "'" in correct_query.split("= ")[-1]
    )  # String types should be enclosed in quotes

    assert (
        type(list(block_data.values())[0]) != str
        and "'" not in correct_query.split("= ")[1]
    )  # Non-string types should not be enclosed in quotes


def test_blocking_data():
    db_name = (
        pathlib.Path(__file__).parent.parent.parent
        / "examples"
        / "MPI-sample-data"
        / "synthetic_patient_mpi_db"
    )

    table_name = "synthetic_patient_mpi"
    block_data = {"ZIP": 90265, "City": "Malibu"}
    blocked_data = block_data_from_db(db_name, table_name, block_data)

    # Assert data is returned
    assert len(blocked_data) > 0
    # Assert returned data is in the correct format
    assert type(blocked_data[0]) == list
    # Assert returned data match the block_data parameters
    assert (
        blocked_data[random.randint(0, len(blocked_data) - 1)][11] == block_data["City"]
    )
    assert (
        blocked_data[random.randint(0, len(blocked_data) - 1)][-4] == block_data["ZIP"]
    )

    # Assert exception is raised when block_data is empty
    block_data = {}
    with pytest.raises(ValueError) as e:
        block_data_from_db(db_name, table_name, block_data)
    assert "`block_data` cannot be empty." in str(e.value)


def test_read_write_m_probs():
    data = pd.read_csv(
        pathlib.Path(__file__).parent.parent / "assets" / "patient_lol.csv",
        index_col=False,
        dtype="object",
        keep_default_na=False,
    )
    true_matches = {
        0: {1, 2, 3},
        1: {2, 3},
        2: {3},
        7: {8, 10, 11},
        8: {10, 11},
        10: {11},
    }
    true_probs = {
        "BIRTHDATE": 1.0,
        "FIRST": 2.0 / 13.0,
        "LAST": 5.0 / 13.0,
        "GENDER": 1.0,
        "ADDRESS": 1.0,
        "CITY": 1.0,
        "STATE": 1.0,
        "ZIP": 1.0,
        "ID": 1.0 / 13.0,
    }
    if os.path.isfile("./m.json"):
        os.remove("./m.json")

    m_probs = calculate_m_probs(data, true_matches, file_to_write="m.json")
    assert m_probs == true_probs

    loaded_probs = load_json_probs("m.json")
    assert loaded_probs == true_probs

    os.remove("./m.json")


def test_read_write_u_probs():
    seed(0)
    data = pd.read_csv(
        pathlib.Path(__file__).parent.parent / "assets" / "patient_lol.csv",
        index_col=False,
        dtype="object",
        keep_default_na=False,
    )
    true_matches = {
        0: {1, 2, 3},
        1: {2, 3},
        2: {3},
        7: {8, 10, 11},
        8: {10, 11},
        10: {11},
    }
    true_probs = {
        "BIRTHDATE": 3.0 / 11.0,
        "FIRST": 1.0 / 11.0,
        "LAST": 2.0 / 11.0,
        "GENDER": 1.0,
        "ADDRESS": 1.0,
        "CITY": 1.0,
        "STATE": 1.0,
        "ZIP": 3.0 / 11.0,
        "ID": 1.0 / 11.0,
    }
    if os.path.isfile("./u.json"):
        os.remove("./u.json")

    u_probs = calculate_u_probs(
        data, true_matches, n_samples=10, file_to_write="u.json"
    )
    assert u_probs == true_probs

    loaded_probs = load_json_probs("u.json")
    assert loaded_probs == true_probs

    os.remove("./u.json")


def test_read_write_log_odds():
    if os.path.isfile("./log_odds.json"):
        os.remove("./log_odds.json")
    m_probs = {"A": 1.0, "B": 0.5, "C": 0.25, "D": 0.125}
    u_probs = {"A": 0.1, "B": 0.2, "C": 0.05, "D": 0.125}
    true_log_odds = {
        "A": log(1.0) - log(0.1),
        "B": log(0.5) - log(0.2),
        "C": log(0.25) - log(0.05),
        "D": log(1),
    }
    log_odds = calculate_log_odds(m_probs, u_probs, file_to_write="log_odds.json")
    assert log_odds == true_log_odds
    loaded_log_odds = load_json_probs("log_odds.json")
    assert loaded_log_odds == true_log_odds

    with pytest.raises(ValueError) as e:
        calculate_log_odds({}, u_probs)
    assert "probability dictionaries must contain the same set of keys" in str(e.value)

    os.remove("log_odds.json")


def test_load_json_probs_errors():
    with pytest.raises(FileNotFoundError) as e:
        load_json_probs("does_not_exist.json")
    assert "specified file does not exist at" in str(e.value)

    with open("not_valid_json.json", "w") as file:
        file.write("I am not valid JSON")
    with pytest.raises(JSONDecodeError) as e:
        load_json_probs("not_valid_json.json")
    assert "specified file is not valid JSON" in str(e.value)

    os.remove("not_valid_json.json")


def test_eval_log_odds_cutoff():
    with pytest.raises(KeyError) as e:
        eval_log_odds_cutoff([])
    assert "Cutoff threshold for true matches must be passed" in str(e.value)

    assert not eval_log_odds_cutoff([], true_match_threshold=10.0)
    assert not eval_log_odds_cutoff([1.0, 0.0, 6.0, 2.7], true_match_threshold=10.0)
    assert eval_log_odds_cutoff([4.3, 6.1, 2.5], true_match_threshold=10.0)


def test_feature_match_log_odds_exact():
    with pytest.raises(KeyError) as e:
        feature_match_log_odds_exact([], [], 0)
    assert "Mapping of indices to column names must be provided" in str(e.value)
    with pytest.raises(KeyError) as e:
        feature_match_log_odds_exact([], [], 0, idx_to_col={})
    assert "Mapping of columns to m/u log-odds must be provided" in str(e.value)

    ri = ["John", "Shepard", "11-07-1980", "1234 Silversun Strip"]
    rj = ["John", 6.0, None, "2345 Goldmoon Ave."]
    idx_to_col = {0: "first", 1: "last", 2: "birthdate", 3: "address"}
    log_odds = {"first": 4.0, "last": 6.5, "birthdate": 9.8, "address": 3.7}

    assert (
        feature_match_log_odds_exact(
            ri, rj, 0, idx_to_col=idx_to_col, log_odds=log_odds
        )
        == 4.0
    )

    for i in range(1, 4):
        assert (
            feature_match_log_odds_exact(
                ri, rj, i, idx_to_col=idx_to_col, log_odds=log_odds
            )
            == 0.0
        )


def test_feature_match_log_odds_fuzzy():
    with pytest.raises(KeyError) as e:
        feature_match_log_odds_fuzzy_compare([], [], 0)
    assert "Mapping of indices to column names must be provided" in str(e.value)
    with pytest.raises(KeyError) as e:
        feature_match_log_odds_fuzzy_compare([], [], 0, idx_to_col={})
    assert "Mapping of columns to m/u log-odds must be provided" in str(e.value)

    ri = ["John", "Shepard", "11-07-1980", "1234 Silversun Strip"]
    rj = ["John", "Sheperd", "06-08-2000", "asdfghjeki"]
    idx_to_col = {0: "first", 1: "last", 2: "birthdate", 3: "address"}
    log_odds = {"first": 4.0, "last": 6.5, "birthdate": 9.8, "address": 3.7}

    assert (
        feature_match_log_odds_fuzzy_compare(
            ri, rj, 0, idx_to_col=idx_to_col, log_odds=log_odds
        )
        == 4.0
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, 1, idx_to_col=idx_to_col, log_odds=log_odds
            ),
            3,
        )
        == 6.129
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, 2, idx_to_col=idx_to_col, log_odds=log_odds
            ),
            3,
        )
        == 5.227
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, 3, idx_to_col=idx_to_col, log_odds=log_odds
            ),
            3,
        )
        == 0.987
    )


def test_algo_read():
    dibbs_basic_algo = read_linkage_config(
        pathlib.Path(__file__).parent.parent.parent
        / "phdi"
        / "linkage"
        / "algorithms"
        / "dibbs_basic.json"
    )
    assert dibbs_basic_algo.get("algorithm", []) == [
        {
            "funcs": {
                0: "feature_match_fuzzy_string",
                2: "feature_match_fuzzy_string",
                3: "feature_match_fuzzy_string",
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": "eval_perfect_match",
            "cluster_ratio": 0.9,
        },
        {
            "funcs": {
                10: "feature_match_fuzzy_string",
                16: "feature_match_fuzzy_string",
            },
            "blocks": ["FIRST4", "LAST4"],
            "matching_rule": "eval_perfect_match",
            "cluster_ratio": 0.9,
        },
    ]

    dibbs_enhanced_algo = read_linkage_config(
        pathlib.Path(__file__).parent.parent.parent
        / "phdi"
        / "linkage"
        / "algorithms"
        / "dibbs_enhanced.json"
    )
    assert dibbs_enhanced_algo.get("algorithm", []) == [
        {
            "funcs": {
                0: "feature_match_log_odds_fuzzy_compare",
                2: "feature_match_log_odds_fuzzy_compare",
                3: "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {
                "similarity_measure": "JaroWinkler",
                "threshold": 0.7,
                "true_match_threshold": 16.5,
            },
        },
        {
            "funcs": {
                10: "feature_match_log_odds_fuzzy_compare",
                16: "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": ["FIRST4", "LAST4"],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {
                "similarity_measure": "JaroWinkler",
                "threshold": 0.7,
                "true_match_threshold": 7.0,
            },
        },
    ]


def test_read_algo_errors():
    with pytest.raises(FileNotFoundError) as e:
        read_linkage_config("invalid.json")
    assert "No file exists at path invalid.json." in str(e.value)
    with open("not_valid_json_test.json", "w") as fp:
        fp.write("this is a random string that is not in json format\n")
    with pytest.raises(JSONDecodeError) as e:
        read_linkage_config("not_valid_json_test.json")
    assert "The specified file is not valid JSON" in str(e.value)
    os.remove("not_valid_json_test.json")


def test_algo_write():
    sample_algo = [
        {
            "funcs": {
                8: feature_match_fuzzy_string,
                12: feature_match_exact,
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": eval_perfect_match,
        },
        {
            "funcs": {
                10: feature_match_four_char,
                16: feature_match_log_odds_exact,
                22: feature_match_log_odds_fuzzy_compare,
            },
            "blocks": ["ZIP", "BIRTH_YEAR"],
            "matching_rule": eval_log_odds_cutoff,
            "cluster_ratio": 0.9,
            "kwargs": {"similarity_measure": "Levenshtein", "threshold": 0.85},
        },
    ]
    test_file_path = "algo_test_write.json"
    if os.path.isfile("./" + test_file_path):  # pragma: no cover
        os.remove("./" + test_file_path)
    write_linkage_config(sample_algo, test_file_path)

    loaded_algo = read_linkage_config(test_file_path)
    assert loaded_algo.get("algorithm", []) == [
        {
            "funcs": {
                8: "feature_match_fuzzy_string",
                12: "feature_match_exact",
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": "eval_perfect_match",
        },
        {
            "funcs": {
                10: "feature_match_four_char",
                16: "feature_match_log_odds_exact",
                22: "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": ["ZIP", "BIRTH_YEAR"],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {"similarity_measure": "Levenshtein", "threshold": 0.85},
        },
    ]
    os.remove("./" + test_file_path)
