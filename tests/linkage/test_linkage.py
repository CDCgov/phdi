import os
import pandas as pd
from phdi.linkage import (
    generate_hash_str,
    block_parquet_data,
    feature_match_exact,
    feature_match_fuzzy_string,
    eval_perfect_match,
    match_within_block,
)
from phdi.linkage.link import _match_within_block_cluster_ratio


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

    blocked_test_data = block_parquet_data(path="./test.parquet", blocks=["zip"])

    # Test output data types are correct
    assert isinstance(blocked_test_data, dict)
    assert isinstance(blocked_test_data[90006], list)

    # Test that the number of blocks is the same as the distinct number of zip codes
    assert len(blocked_test_data.keys()) == test_data_df["zip"].nunique()

    # Test blocks with multiple block columns
    blocked_test_data = block_parquet_data(
        path="./test.parquet", blocks=["zip", "year_of_birth"]
    )
    assert len(blocked_test_data[(90210, 1992)]) == 2

    # Clean up
    if os.path.isfile("./test.parquet"):  # pragma: no cover
        os.remove("./test.parquet")
