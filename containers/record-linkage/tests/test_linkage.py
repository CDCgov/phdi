import copy
import json
import os
import pathlib
import uuid
from datetime import date
from datetime import datetime
from json.decoder import JSONDecodeError

import pytest
from app.linkage.algorithms import DIBBS_BASIC
from app.linkage.algorithms import DIBBS_ENHANCED
from app.linkage.dal import DataAccessLayer
from app.linkage.link import _compare_address_elements
from app.linkage.link import _compare_name_elements
from app.linkage.link import _condense_extract_address_from_resource
from app.linkage.link import _convert_given_name_to_first_name
from app.linkage.link import _flatten_patient_resource
from app.linkage.link import _get_fuzzy_params
from app.linkage.link import _match_within_block_cluster_ratio
from app.linkage.link import add_person_resource
from app.linkage.link import eval_log_odds_cutoff
from app.linkage.link import eval_perfect_match
from app.linkage.link import extract_blocking_values_from_record
from app.linkage.link import feature_match_exact
from app.linkage.link import feature_match_four_char
from app.linkage.link import feature_match_fuzzy_string
from app.linkage.link import feature_match_log_odds_exact
from app.linkage.link import feature_match_log_odds_fuzzy_compare
from app.linkage.link import generate_hash_str
from app.linkage.link import link_record_against_mpi
from app.linkage.link import load_json_probs
from app.linkage.link import match_within_block
from app.linkage.link import read_linkage_config
from app.linkage.link import score_linkage_vs_truth
from app.linkage.link import write_linkage_config
from app.linkage.mpi import DIBBsMPIConnectorClient
from app.utils import _clean_up
from sqlalchemy import select
from sqlalchemy import text


def _init_db() -> DataAccessLayer:
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
    _clean_up(dal)

    # load ddl
    schema_ddl = open(
        pathlib.Path(__file__).parent.parent.parent.parent
        / "containers"
        / "record-linkage"
        / "migrations"
        / "V01_01__flat_schema.sql"
    ).read()

    try:
        with dal.engine.connect() as db_conn:
            db_conn.execute(text(schema_ddl))
            db_conn.commit()
    except Exception as e:
        print(e)
        with dal.engine.connect() as db_conn:
            db_conn.rollback()
    dal.initialize_schema()

    return DIBBsMPIConnectorClient()


def test_extract_blocking_values_from_record():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent.parent
            / "containers"
            / "record-linkage"
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    patient = [
        r.get("resource")
        for r in bundle.get("entry")
        if r.get("resource", {}).get("resourceType") == "Patient"
    ][0]
    patient["name"][0]["family"] = "Shepard"

    with pytest.raises(KeyError) as e:
        extract_blocking_values_from_record(patient, {"invalid"})
    assert "Input dictionary for block" in str(e.value)

    with pytest.raises(ValueError) as e:
        extract_blocking_values_from_record(patient, [{"value": "invalid"}])
    assert "is not a supported extraction field" in str(e.value)

    with pytest.raises(ValueError) as e:
        extract_blocking_values_from_record(
            patient, [{"value": "first_name", "transformation": "invalid_transform"}]
        )
    assert "Transformation invalid_transform is not valid" in str(e.value)

    blocking_fields = [
        {"value": "first_name", "transformation": "first4"},
        {"value": "last_name", "transformation": "first4"},
        {"value": "zip"},
        {"value": "city"},
        {"value": "birthdate"},
        {"value": "sex"},
        {"value": "state"},
        {"value": "address", "transformation": "last4"},
    ]
    blocking_vals = extract_blocking_values_from_record(
        patient,
        blocking_fields,
    )
    assert blocking_vals == {
        "first_name": {"value": "John", "transformation": "first4"},
        "last_name": {"value": "Shep", "transformation": "first4"},
        "zip": {"value": "10001-0001"},
        "city": {"value": "Faketon"},
        "birthdate": {"value": "1983-02-01"},
        "sex": {"value": "female"},
        "state": {"value": "NY"},
        "address": {"value": "e St", "transformation": "last4"},
    }

    patient["birthDate"] = ""
    patient["name"][0]["family"] = None

    blocking_vals = extract_blocking_values_from_record(
        patient,
        blocking_fields,
    )
    assert blocking_vals == {
        "first_name": {"value": "John", "transformation": "first4"},
        "zip": {"value": "10001-0001"},
        "city": {"value": "Faketon"},
        "sex": {"value": "female"},
        "state": {"value": "NY"},
        "address": {"value": "e St", "transformation": "last4"},
    }


def test_generate_hash():
    salt_str = "super-legit-salt"
    patient_1 = (
        "John-Shepard-2153/11/07-1234 Silversun Strip Boston Massachusetts 99999"
    )
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"

    hash_1 = generate_hash_str(patient_1, salt_str)
    hash_2 = generate_hash_str(patient_2, salt_str)

    assert hash_1 == "b124335071679e95341b8133669f6ab475f211f3e19d3cf69e7b6f13b0df45d6"
    assert hash_2 == "102818c623290c24069beb721c6eb465d281b3b67ecfb6aef924d14affa117b9"


def test_feature_match_exact():
    record_i = [1, 0, -1, "blah", "", True]
    record_j = [1, 0, -1, "blah", "", True]
    record_k = [2, 10, -10, "no match", "null", False]

    cols = {"col_1": 0, "col_2": 1, "col_3": 2, "col_4": 3, "col_5": 4, "col_6": 5}

    # Simultaneously test matches and non-matches of different data types
    for c in cols:
        assert feature_match_exact(record_i, record_j, c, cols)
        assert not feature_match_exact(record_i, record_k, c, cols)

    # Special case for matching None--None == None is vacuous
    assert feature_match_exact([None], [None], "col_7", {"col_7": 0})


def test_get_fuzzy_params():
    kwargs = {
        "similarity_measure": "Levenshtein",
        "thresholds": {"city": 0.95, "address": 0.98},
    }

    assert _get_fuzzy_params("city", **kwargs) == ("Levenshtein", 0.95)
    assert _get_fuzzy_params("address", **kwargs) == ("Levenshtein", 0.98)
    assert _get_fuzzy_params("first_name", **kwargs) == ("Levenshtein", 0.7)

    del kwargs["similarity_measure"]

    assert _get_fuzzy_params("last_name", **kwargs) == ("JaroWinkler", 0.7)


def test_feature_match_fuzzy_string():
    record_i = ["string1", "John", "John", "1985-12-12", None]
    record_j = ["string2", "Jhon", "Jon", "1985-12-12", None]

    cols = {"col_1": 0, "col_2": 1, "col_3": 2, "col_4": 3}

    for c in cols:
        assert feature_match_fuzzy_string(
            record_i,
            record_j,
            c,
            cols,
            similarity_measure="JaroWinkler",
            threshold=0.7,
        )
    assert not feature_match_fuzzy_string(
        ["no match"],
        ["dont match me bro"],
        "col_5",
        {"col_5": 0},
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
        "first_name": feature_match_fuzzy_string,
        "last_name": feature_match_fuzzy_string,
        "birthdate": feature_match_exact,
        "zip": feature_match_exact,
    }
    col_to_idx = {"first_name": 1, "last_name": 2, "birthdate": 3, "zip": 4}

    # Do a test run requiring total membership match
    matches = _match_within_block_cluster_ratio(
        data, 1.0, funcs, col_to_idx, eval_rule, threshold=0.8
    )
    assert matches == [{0, 1, 2}, {3}, {4}, {5}, {6}, {7, 8, 10}, {9}, {11}]

    # Now do a test showing different cluster groupings
    matches = _match_within_block_cluster_ratio(
        data, 0.6, funcs, col_to_idx, eval_rule, threshold=0.8
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
        "first_name": feature_match_exact,
        "last_name": feature_match_exact,
        "birthdate": feature_match_exact,
        "zip": feature_match_exact,
    }
    col_to_idx = {"first_name": 1, "last_name": 2, "birthdate": 3, "zip": 4}
    match_pairs = match_within_block(data, funcs, col_to_idx, eval_rule)
    assert len(match_pairs) == 0

    # Now, require exact on DOB and zip, but allow fuzzy on first and last
    # Expect 6 matches
    funcs["first_name"] = feature_match_fuzzy_string
    funcs["last_name"] = feature_match_fuzzy_string
    match_pairs = match_within_block(data, funcs, col_to_idx, eval_rule)
    assert match_pairs == [(0, 1), (0, 2), (1, 2), (5, 6), (5, 8), (6, 8)]

    # As above, but let's be explicit about string comparison and threshold
    # Expect three matches, but none with the "Johns"
    # Note the difference in returned results by changing distance function
    match_pairs = match_within_block(
        data,
        funcs,
        col_to_idx,
        eval_rule,
        similarity_measure="Levenshtein",
        threshold=0.8,
    )
    assert match_pairs == [(5, 6), (5, 8), (6, 8)]


def test_feature_match_four_char():
    record_i = ["Johnathan", "Shepard"]
    record_j = ["John", "Sheperd"]
    record_k = ["Jhon", "Sehpard"]

    cols = {"first": 0, "last": 1}

    # Simultaneously test matches and non-matches of different data types
    for c in cols:
        assert feature_match_four_char(record_i, record_j, c, cols)
        assert not feature_match_four_char(record_i, record_k, c, cols)


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
        feature_match_log_odds_exact([], [], "c", {})
    assert "Mapping of columns to m/u log-odds must be provided" in str(e.value)

    ri = ["John", "Shepard", "11-07-1980", "1234 Silversun Strip"]
    rj = ["John", 6.0, None, "2345 Goldmoon Ave."]
    col_to_idx = {"first": 0, "last": 1, "birthdate": 2, "address": 3}
    log_odds = {"first": 4.0, "last": 6.5, "birthdate": 9.8, "address": 3.7}

    assert (
        feature_match_log_odds_exact(ri, rj, "first", col_to_idx, log_odds=log_odds)
        == 4.0
    )

    for c in col_to_idx:
        if c != "first":
            assert (
                feature_match_log_odds_exact(ri, rj, c, col_to_idx, log_odds=log_odds)
                == 0.0
            )


def test_feature_match_log_odds_fuzzy():
    with pytest.raises(KeyError) as e:
        feature_match_log_odds_fuzzy_compare([], [], "c", {})
    assert "Mapping of columns to m/u log-odds must be provided" in str(e.value)

    ri = ["John", "Shepard", date(1980, 11, 7), "1234 Silversun Strip"]
    rj = ["John", "Sheperd", datetime(1970, 6, 7), "asdfghjeki"]
    col_to_idx = {"first": 0, "last": 1, "birthdate": 2, "address": 3}
    log_odds = {"first": 4.0, "last": 6.5, "birthdate": 9.8, "address": 3.7}

    assert (
        feature_match_log_odds_fuzzy_compare(
            ri, rj, "first", col_to_idx, log_odds=log_odds
        )
        == 4.0
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, "last", col_to_idx, log_odds=log_odds
            ),
            3,
        )
        == 6.129
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, "birthdate", col_to_idx, log_odds=log_odds
            ),
            3,
        )
        == 7.859
    )

    assert (
        round(
            feature_match_log_odds_fuzzy_compare(
                ri, rj, "address", col_to_idx, log_odds=log_odds
            ),
            3,
        )
        == 0.0
    )


def test_algo_read():
    dibbs_basic_algo = read_linkage_config(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "linkage"
        / "dibbs_basic_algorithm.json"
    )
    assert dibbs_basic_algo == [
        {
            "funcs": {
                "first_name": "feature_match_fuzzy_string",
                "last_name": "feature_match_exact",
            },
            "blocks": [
                {"value": "birthdate"},
                {"value": "mrn", "transformation": "last4"},
                {"value": "sex"},
            ],
            "matching_rule": "eval_perfect_match",
            "cluster_ratio": 0.9,
            "kwargs": {
                "thresholds": {
                    "first_name": 0.9,
                    "last_name": 0.9,
                    "birthdate": 0.95,
                    "address": 0.9,
                    "city": 0.92,
                    "zip": 0.95,
                }
            },
        },
        {
            "funcs": {
                "address": "feature_match_fuzzy_string",
                "birthdate": "feature_match_exact",
            },
            "blocks": [
                {"value": "zip"},
                {"value": "first_name", "transformation": "first4"},
                {"value": "last_name", "transformation": "first4"},
                {"value": "sex"},
            ],
            "matching_rule": "eval_perfect_match",
            "cluster_ratio": 0.9,
            "kwargs": {
                "thresholds": {
                    "first_name": 0.9,
                    "last_name": 0.9,
                    "birthdate": 0.95,
                    "address": 0.9,
                    "city": 0.92,
                    "zip": 0.95,
                }
            },
        },
    ]

    dibbs_enhanced_algo = read_linkage_config(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "linkage"
        / "dibbs_enhanced_algorithm.json"
    )
    assert dibbs_enhanced_algo == [
        {
            "funcs": {
                "first_name": "feature_match_log_odds_fuzzy_compare",
                "last_name": "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": [
                {"value": "birthdate"},
                {"value": "mrn", "transformation": "last4"},
                {"value": "sex"},
            ],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {
                "similarity_measure": "JaroWinkler",
                "thresholds": {
                    "first_name": 0.9,
                    "last_name": 0.9,
                    "birthdate": 0.95,
                    "address": 0.9,
                    "city": 0.92,
                    "zip": 0.95,
                },
                "true_match_threshold": 12.2,
                "log_odds": {
                    "address": 8.438284928858774,
                    "birthdate": 10.126641103800338,
                    "city": 2.438553006137189,
                    "first_name": 6.849475906891162,
                    "last_name": 6.350720397426025,
                    "mrn": 0.3051262572525359,
                    "sex": 0.7510419059643679,
                    "state": 0.022376768992488694,
                    "zip": 4.975031471124867,
                },
            },
        },
        {
            "funcs": {
                "address": "feature_match_log_odds_fuzzy_compare",
                "birthdate": "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": [
                {"value": "zip"},
                {"value": "first_name", "transformation": "first4"},
                {"value": "last_name", "transformation": "first4"},
                {"value": "sex"},
            ],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {
                "similarity_measure": "JaroWinkler",
                "thresholds": {
                    "first_name": 0.9,
                    "last_name": 0.9,
                    "birthdate": 0.95,
                    "address": 0.9,
                    "city": 0.92,
                    "zip": 0.95,
                },
                "true_match_threshold": 17.0,
                "log_odds": {
                    "address": 8.438284928858774,
                    "birthdate": 10.126641103800338,
                    "city": 2.438553006137189,
                    "first_name": 6.849475906891162,
                    "last_name": 6.350720397426025,
                    "mrn": 0.3051262572525359,
                    "sex": 0.7510419059643679,
                    "state": 0.022376768992488694,
                    "zip": 4.975031471124867,
                },
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
                "first_name": feature_match_fuzzy_string,
                "last_name": feature_match_exact,
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": eval_perfect_match,
        },
        {
            "funcs": {
                "last_name": feature_match_four_char,
                "sex": feature_match_log_odds_exact,
                "address": feature_match_log_odds_fuzzy_compare,
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
    assert loaded_algo == [
        {
            "funcs": {
                "first_name": "feature_match_fuzzy_string",
                "last_name": "feature_match_exact",
            },
            "blocks": ["MRN4", "ADDRESS4"],
            "matching_rule": "eval_perfect_match",
        },
        {
            "funcs": {
                "last_name": "feature_match_four_char",
                "sex": "feature_match_log_odds_exact",
                "address": "feature_match_log_odds_fuzzy_compare",
            },
            "blocks": ["ZIP", "BIRTH_YEAR"],
            "matching_rule": "eval_log_odds_cutoff",
            "cluster_ratio": 0.9,
            "kwargs": {"similarity_measure": "Levenshtein", "threshold": 0.85},
        },
    ]
    os.remove("./" + test_file_path)


def test_link_record_against_mpi_none_record():
    algorithm = DIBBS_BASIC
    MPI = _init_db()

    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )

    patients = patients["entry"]
    patients = [
        p.get("resource")
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ][:2]

    # Test various null data values in incoming record
    patients[1]["gender"] = None
    patients[1]["zip"] = None
    matches = []
    mapped_patients = {}
    for patient in patients:
        matched, pid = link_record_against_mpi(
            patient,
            algorithm,
        )
        matches.append(matched)
        if str(pid) not in mapped_patients:
            mapped_patients[str(pid)] = 0
        mapped_patients[str(pid)] += 1

    # First patient inserted into empty MPI, no match
    # Second patient blocks with first patient in first pass, then fuzzy matches name
    assert matches == [False, True]
    assert sorted(list(mapped_patients.values())) == [2]

    _clean_up(MPI.dal)


# TODO: Move this to an integration test suite
def test_link_record_against_mpi():
    algorithm = DIBBS_BASIC
    MPI = _init_db()
    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    patients = patients["entry"]
    patients = [
        p
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ]

    matches = []
    mapped_patients = {}
    for patient in patients:
        matched, pid = link_record_against_mpi(
            patient["resource"],
            algorithm,
        )
        matches.append(matched)
        if str(pid) not in mapped_patients:
            mapped_patients[str(pid)] = 0
        mapped_patients[str(pid)] += 1

    # First patient inserted into empty MPI, no match
    # Second patient blocks with first patient in first pass, then fuzzy matches name
    # Third patient is entirely new individual, no match
    # Fourth patient fails blocking with first pass then fails on second
    # Fifth patient: in first pass MRN blocks with one cluster but fails name,
    # in second pass name blocks with different cluster but fails address, no match
    # Sixth patient: in first pass, MRN blocks with one cluster and name matches in it,
    # in second pass name blocks on different cluster and address matches it,
    # finds greatest strength match and correctly assigns to larger cluster
    assert matches == [False, True, False, False, False, False]
    assert sorted(list(mapped_patients.values())) == [1, 1, 1, 1, 2]

    # Re-open connection to check for all insertions
    patient_records = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))
    patient_id_count = {}
    person_id_count = {}
    for patient in patient_records[1:]:
        if str(patient[0]) not in patient_id_count:
            patient_id_count[str(patient[0])] = 1
        else:
            patient_id_count[str(patient[0])] = patient_id_count[str(patient[0])] + 1
        if str(patient[1]) not in person_id_count:
            person_id_count[str(patient[1])] = 1
        else:
            person_id_count[str(patient[1])] = person_id_count[str(patient[1])] + 1

    assert len(patient_records[1:]) == len(patients)
    for person_id in person_id_count:
        assert person_id_count[person_id] == mapped_patients[person_id]

    # name and given_name
    given_name_count = 0
    name_count = 0
    for patient in patients:
        for name in patient["resource"]["name"]:
            name_count += 1
            for given_name in name["given"]:
                given_name_count += 1
    given_name_records = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE))
    assert len(given_name_records[1:]) == given_name_count
    name_records = MPI.dal.select_results(select(MPI.dal.NAME_TABLE))
    assert len(name_records[1:]) == name_count

    # address
    address_records = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE))
    address_count = 0
    for patient in patients:
        for address in patient["resource"]["address"]:
            address_count += 1
    assert len(address_records[1:]) == address_count

    _clean_up(MPI.dal)


def test_link_record_against_mpi_enhanced_algo():
    algorithm = DIBBS_ENHANCED
    MPI = _init_db()
    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    patients = patients["entry"]
    patients = [
        p
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ]
    # add an additional patient that will fuzzy match to patient 0
    patient0_copy = copy.deepcopy(patients[0])
    patient0_copy["resource"]["id"] = str(uuid.uuid4())
    patient0_copy["resource"]["name"][0]["given"][0] = "Jhon"
    patients.append(patient0_copy)
    matches = []
    mapped_patients = {}
    for patient in patients:
        matched, pid = link_record_against_mpi(
            patient["resource"],
            algorithm,
        )
        matches.append(matched)
        if str(pid) not in mapped_patients:
            mapped_patients[str(pid)] = 0
        mapped_patients[str(pid)] += 1

    # First patient inserted into empty MPI, no match
    # Second patient blocks with first patient in first pass, then fuzzy matches name
    # Third patient is entirely new individual, no match
    # Fourth patient fails blocking with first pass but catches on second, fuzzy matches
    # Fifth patient: in first pass MRN blocks with one cluster but fails name,
    #  in second pass name blocks with different cluster but fails address, no match
    # Sixth patient: in first pass, MRN blocks with one cluster and name matches in it,
    # in second pass name blocks on different cluster and address matches it,
    #  finds greatest strength match and correctly assigns to larger cluster
    assert matches == [False, True, False, True, False, False, True]
    assert sorted(list(mapped_patients.values())) == [1, 1, 1, 4]

    # Re-open connection to check for all insertions
    patient_records = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))
    patient_id_count = {}
    person_id_count = {}
    for patient in patient_records[1:]:
        if str(patient[0]) not in patient_id_count:
            patient_id_count[str(patient[0])] = 1
        else:
            patient_id_count[str(patient[0])] = patient_id_count[str(patient[0])] + 1
        if str(patient[1]) not in person_id_count:
            person_id_count[str(patient[1])] = 1
        else:
            person_id_count[str(patient[1])] = person_id_count[str(patient[1])] + 1

    assert len(patient_records[1:]) == len(patients)
    for person_id in person_id_count:
        assert person_id_count[person_id] == mapped_patients[person_id]

    # name and given_name
    given_name_count = 0
    name_count = 0
    for patient in patients:
        for name in patient["resource"]["name"]:
            name_count += 1
            for given_name in name["given"]:
                given_name_count += 1
    given_name_records = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE))
    assert len(given_name_records[1:]) == given_name_count
    name_records = MPI.dal.select_results(select(MPI.dal.NAME_TABLE))
    assert len(name_records[1:]) == name_count

    # address
    address_records = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE))
    address_count = 0
    for patient in patients:
        for address in patient["resource"]["address"]:
            address_count += 1
    assert len(address_records[1:]) == address_count

    _clean_up(MPI.dal)


def test_add_person_resource():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent.parent
            / "containers"
            / "record-linkage"
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    raw_bundle = copy.deepcopy(bundle)
    patient_id = "TEST_PATIENT_ID"
    person_id = "TEST_PERSON_ID"

    returned_bundle = add_person_resource(
        person_id=person_id, patient_id=patient_id, bundle=raw_bundle
    )

    # Assert returned_bundle has added element in "entry"
    assert len(returned_bundle.get("entry")) == len(bundle.get("entry")) + 1

    # Assert the added element is the person_resource bundle
    assert (
        returned_bundle.get("entry")[-1].get("resource").get("resourceType") == "Person"
    )
    assert (
        returned_bundle.get("entry")[-1].get("request").get("url")
        == "Person/TEST_PERSON_ID"
    )


def test_compare_address_elements():
    feature_funcs = {
        "address": feature_match_four_char,
    }
    col_to_idx = {"address": 2}
    record = [
        "123",
        "1",
        ["John", "Paul", "George"],
        "1980-01-01",
        ["123 Main St"],
    ]
    record2 = [
        "123",
        "1",
        ["John", "Paul", "George"],
        "1980-01-01",
        ["123 Main St", "9 North Ave"],
    ]
    mpi_patient1 = [
        "456",
        "2",
        "John",
        "1980-01-01",
        "123 Main St",
    ]
    mpi_patient2 = [
        "789",
        "3",
        "Pierre",
        "1980-01-01",
        "6 South St",
    ]

    same_address = _compare_address_elements(
        record, mpi_patient1, feature_funcs, "address", col_to_idx
    )
    assert same_address is True

    same_address = _compare_address_elements(
        record2, mpi_patient1, feature_funcs, "address", col_to_idx
    )
    assert same_address is True

    different_address = _compare_address_elements(
        record, mpi_patient2, feature_funcs, "address", col_to_idx
    )
    assert different_address is False


def test_compare_name_elements():
    feature_funcs = {"first": feature_match_fuzzy_string}
    col_to_idx = {"first": 0}
    record = [
        "123",
        "1",
        ["John", "Paul", "George"],
        "1980-01-01",
        ["123 Main St"],
    ]
    record3 = [
        "123",
        "1",
        ["Jean", "Pierre"],
        "1980-01-01",
        ["123 Main St", "9 North Ave"],
    ]
    mpi_patient1 = [
        "456",
        "2",
        "John",
        "1980-01-01",
        "756 South St",
    ]
    mpi_patient2 = [
        "789",
        "3",
        "Jean",
        "1980-01-01",
        "6 South St",
    ]

    same_name = _compare_name_elements(
        record[2:], mpi_patient1[2:], feature_funcs, "first", col_to_idx
    )
    assert same_name is True

    # Assert same first name with new middle name in record == true fuzzy match
    add_middle_name = _compare_name_elements(
        record3[2:], mpi_patient2[2:], feature_funcs, "first", col_to_idx
    )
    assert add_middle_name is True

    add_middle_name = _compare_name_elements(
        record[2:], mpi_patient1[2:], feature_funcs, "first", col_to_idx
    )
    assert add_middle_name is True

    # Assert no match with different names
    different_names = _compare_name_elements(
        record3[2:], mpi_patient1[2:], feature_funcs, "first", col_to_idx
    )
    assert different_names is False


def test_condense_extracted_address():
    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    patients = patients["entry"]
    patients = [
        p.get("resource", {})
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ]
    patient = patients[2]
    assert _condense_extract_address_from_resource(patient, "address") == [
        "PO Box 1 First Rock",
        "Bay 16 Ward Sector 24",
    ]


def test_flatten_patient():
    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )

    patients = patients["entry"]
    patients = [
        p.get("resource", {})
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ]

    col_to_idx = {
        "address": 0,
        "birthdate": 1,
        "city": 2,
        "first_name": 3,
        "last_name": 4,
        "mrn": 4,
        "sex": 5,
        "state": 6,
        "zip": 7,
    }

    # Use patient with multiple identifiers to also test MRN-specific filter
    assert _flatten_patient_resource(patients[2], col_to_idx) == [
        "2c6d5fd1-4a70-11eb-99fd-ad786a821574",
        None,
        ["PO Box 1 First Rock", "Bay 16 Ward Sector 24"],
        "2060-05-14",
        ["Bozeman", "Brooklyn"],
        ["Tali", "Zora", "Tali", "Zora", "Tali", "Zora"],
        "Vas Normandy",
        "7894561235",
        "female",
        ["Montana", "New York"],
        ["11111", "11111"],
    ]


def test_multi_element_blocking():
    MPI = _init_db()
    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    patients = patients["entry"]
    patients = [
        p.get("resource", {})
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ]

    # Insert multi-entry patient into DB
    patient = patients[2]
    algorithm = DIBBS_BASIC
    link_record_against_mpi(patient, algorithm)

    # Now check that we can block on either name & return same results
    # First row of returned results is headers
    vm_found_records = MPI.get_block_data({"last_name": {"value": "Vas Neema"}})
    nr_found_records = MPI.get_block_data({"last_name": {"value": "Nar Raya"}})
    assert vm_found_records == nr_found_records

    _clean_up(MPI.dal)


def test_convert_given_name_to_first_name():
    assert (
        _convert_given_name_to_first_name([]) == []
    ), "Empty data should return empty data"

    data = [["last_name"], ["LENNON"], ["MCCARTNEY"], ["HARRISON"], ["STARKLEY"]]
    assert (
        _convert_given_name_to_first_name(data) == data
    ), "Data without given names should return the same data"

    data = [
        [
            "mrn",
            "last_name",
            "given_name",
            "city",
        ],
        ["111111111", "LENNON", ["JOHN", "WINSTON", "ONO"], "Liverpool"],
        ["222222222", "MCCARTNEY", ["JAMES", "PAUL"], "Liverpool"],
        ["333333333", "HARRISON", ["GEORGE", "HAROLD"], "Liverpool"],
        ["444444444", "STARKLEY", ["RICHARD"], "Liverpool"],
    ]
    assert _convert_given_name_to_first_name(data) == [
        [
            "mrn",
            "last_name",
            "first_name",
            "city",
        ],
        ["111111111", "LENNON", "JOHN WINSTON ONO", "Liverpool"],
        ["222222222", "MCCARTNEY", "JAMES PAUL", "Liverpool"],
        ["333333333", "HARRISON", "GEORGE HAROLD", "Liverpool"],
        ["444444444", "STARKLEY", "RICHARD", "Liverpool"],
    ], "Given names should be concatenated into a single string"
