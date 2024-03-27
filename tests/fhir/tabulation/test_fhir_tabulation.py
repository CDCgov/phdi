import csv
import json
import os.path
import pathlib
import urllib.parse
from unittest import mock

import pytest
import yaml
from requests.models import Response

from phdi.fhir.tabulation.tables import _build_reference_dicts
from phdi.fhir.tabulation.tables import _dereference_included_resource
from phdi.fhir.tabulation.tables import _generate_search_url
from phdi.fhir.tabulation.tables import _generate_search_urls
from phdi.fhir.tabulation.tables import _get_reference_directions
from phdi.fhir.tabulation.tables import _merge_include_query_params_for_location
from phdi.fhir.tabulation.tables import drop_invalid
from phdi.fhir.tabulation.tables import extract_data_from_fhir_search
from phdi.fhir.tabulation.tables import extract_data_from_fhir_search_incremental
from phdi.fhir.tabulation.tables import extract_data_from_schema
from phdi.fhir.tabulation.tables import generate_tables
from phdi.fhir.tabulation.tables import tabulate_data


def test_tabulate_data_invalid_table_name():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )

    with pytest.raises(KeyError):
        tabulate_data(extracted_data["entry"], schema, "")
    with pytest.raises(KeyError):
        tabulate_data(extracted_data["entry"], schema, "invalid name")


def test_tabulate_data():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )

    tabulated_patient_data = tabulate_data(extracted_data["entry"], schema, "Patients")
    tabulated_exam_data = tabulate_data(
        extracted_data["entry"], schema, "Physical Exams"
    )

    # Check all columns from schema present
    assert set(tabulated_patient_data[0]) == {
        "Patient ID",
        "First Name",
        "Last Name",
        "Phone Number",
        "Building Number",
    }
    assert set(tabulated_exam_data[0]) == {
        "Last Name",
        "City",
        "Exam ID",
        "General Practitioner",
    }

    # Check Patients data table
    row_sets = [
        {
            "Kimberley248",
            "Price929",
            "555-690-3898",
            "907844f6-7c99-eabc-f68e-d92189729a55",
            "165",
        },
        {"65489-asdf5-6d8w2-zz5g8", "John", "Shepard", None, 1234},
        {"some-uuid", "John ", None, "123-456-7890", 123},
    ]
    assert len(tabulated_patient_data[1:]) == 3
    tests_run = 0
    for row in row_sets:
        found_match = False
        for table_row in tabulated_patient_data[1:]:
            if set(table_row) == row:
                found_match = True
                break
        if tests_run <= 2:
            tests_run += 1
            assert found_match

    # Check Physical Exams data table
    row_lists = [
        [
            "Waltham",
            "Price929",
            "i-am-not-a-robot",
            ["obs1"],
        ],
        ["no-srsly-i-am-hoomun", "Boston", "Shepard", None],
        ["Faketon", None, None, ["obs2", "obs3"]],
    ]
    assert len(tabulated_exam_data[1:]) == 3
    tests_run = 0
    for row in row_lists:
        found_match = False
        for table_row in tabulated_exam_data[1:]:
            checked_elements = 0
            for element in row:
                if element in table_row:
                    checked_elements += 1
            if checked_elements == len(row) == len(table_row):
                found_match = True
                break
        if tests_run <= 2:
            tests_run += 1
            assert found_match

    # Now test case where the anchor resource type references other
    # resources of the same type that shouldn't generate rows
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "observation_reference_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_observation_data.json"
        )
    )

    tabulated_data = tabulate_data(extracted_data["entry"], schema, "BMI Values")
    assert set(tabulated_data[0]) == {
        "Base Observation ID",
        "BMI",
        "Patient Height",
        "Patient Weight",
    }

    row_sets = [
        {"obs1", 26, 70, 187},
        {"obs2", 34, 63, 132},
    ]
    assert len(tabulated_data[1:]) == 2
    tests_run = 0
    for row in row_sets:
        found_match = False
        for table_row in tabulated_data[1:]:
            if set(table_row) == row:
                found_match = True
                break
        if tests_run <= 1:
            tests_run += 1
            assert found_match


def test_get_reference_directions():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )

    ref_dicts = _get_reference_directions(schema)
    assert ref_dicts == {
        "Patients": {"anchor": "Patient", "forward": set(), "reverse": {}},
        "Physical Exams": {
            "anchor": "Patient",
            "forward": {"Practitioner"},
            "reverse": {"Observation": "Observation:subject"},
        },
    }


def test_build_reference_dicts():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    ref_directions = _get_reference_directions(schema)

    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    ref_dicts = _build_reference_dicts(extracted_data["entry"], ref_directions)
    assert set(ref_dicts.keys()) == {"Patients", "Physical Exams"}
    assert len(ref_dicts["Patients"]["Patient"]) == 3
    assert set(ref_dicts["Patients"]["Patient"].keys()) == {
        "some-uuid",
        "907844f6-7c99-eabc-f68e-d92189729a55",
        "65489-asdf5-6d8w2-zz5g8",
    }
    assert "Observation" not in ref_dicts["Patients"]

    assert len(ref_dicts["Physical Exams"]["Patient"]) == 3
    assert len(ref_dicts["Physical Exams"]["Observation"]) == 2
    assert set(ref_dicts["Physical Exams"]["Observation"].keys()) == {
        "907844f6-7c99-eabc-f68e-d92189729a55",
        "some-uuid",
    }
    assert set(
        [x["id"] for x in ref_dicts["Physical Exams"]["Observation"]["some-uuid"]]
    ) == {
        "obs2",
        "obs3",
    }
    assert len(ref_dicts["Physical Exams"]["Practitioner"]) == 2


def test_dereference_included_resource():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    ref_directions = _get_reference_directions(schema)
    ref_dicts = _build_reference_dicts(data["entry"], ref_directions)

    anchor_resource = data.get("entry")[0].get("resource")
    path_to_use = "Observation.id"
    referenced_resource = data.get("entry")[1].get("resource")
    columns_in_table = schema.get("tables").get("Physical Exams").get("columns")
    column_params = columns_in_table.get("Exam ID")

    assert _dereference_included_resource(
        anchor_resource,
        path_to_use,
        anchor_resource,
        column_params,
        ref_dicts,
        "Physical Exams",
    ) == [referenced_resource]

    path_to_use = "Practitioner.name"
    column_params = columns_in_table.get("General Practitioner")
    referenced_resource = data.get("entry")[6].get("resource")

    assert (
        _dereference_included_resource(
            anchor_resource,
            path_to_use,
            anchor_resource,
            column_params,
            ref_dicts,
            "Physical Exams",
        )
        == referenced_resource
    )

    anchor_resource = data.get("entry")[2].get("resource")
    path_to_use = "Observation.id"
    column_params = columns_in_table.get("Exam ID")

    assert (
        _dereference_included_resource(
            anchor_resource,
            path_to_use,
            anchor_resource,
            column_params,
            ref_dicts,
            "Physical Exams",
        )
        is None
    )


def test_generate_search_url():
    base_fhir_url = "https://fhir-host/r4"

    test_search_url_1 = urllib.parse.quote(
        "Patient?birtdate=2000-01-01T00:00:00", safe="?="
    )
    assert (
        _generate_search_url(f"{base_fhir_url}/{test_search_url_1}")
        == f"{base_fhir_url}/{test_search_url_1}"
    )
    assert _generate_search_url(f"/{test_search_url_1}") == f"/{test_search_url_1}"
    assert _generate_search_url(f"{test_search_url_1}") == f"{test_search_url_1}"
    assert (
        _generate_search_url(f"{test_search_url_1}", default_count=5)
        == f"{test_search_url_1}&_count=5"
    )
    assert (
        _generate_search_url(f"{test_search_url_1}&_count=10", default_count=5)
        == f"{test_search_url_1}&_count=10"
    )
    assert (
        _generate_search_url(
            f"{test_search_url_1}&_count=10", default_since="2022-01-01T00:00:00"
        )
        == f"{test_search_url_1}"
        + f"{urllib.parse.quote('&_count=10&_since=2022-01-01T00:00:00', safe='&=')}"
    )

    test_search_url_2 = "Patient"
    assert (
        _generate_search_url(f"{base_fhir_url}/{test_search_url_2}")
        == f"{base_fhir_url}/{test_search_url_2}"
    )
    assert _generate_search_url(f"/{test_search_url_2}") == f"/{test_search_url_2}"
    assert _generate_search_url(f"{test_search_url_2}") == f"{test_search_url_2}"
    assert (
        _generate_search_url(f"{test_search_url_2}", default_count=5)
        == f"{test_search_url_2}?_count=5"
    )
    assert (
        _generate_search_url(f"{test_search_url_2}?_count=10", default_count=5)
        == f"{test_search_url_2}?_count=10"
    )
    assert (
        _generate_search_url(
            f"{test_search_url_2}?_count=10", default_since="2022-01-01T00:00:00"
        )
        == f"{test_search_url_2}"
        + f"{urllib.parse.quote('?_count=10&_since=2022-01-01T00:00:00', safe='?&=')}"
    )

    test_search_url_3 = urllib.parse.quote(
        "Observation?"
        + "category=http://hl7.org/fhir/ValueSet/observation-category|laboratory",
        safe="?=",
    )
    assert (
        _generate_search_url(f"{base_fhir_url}/{test_search_url_3}")
        == f"{base_fhir_url}/{test_search_url_3}"
    )
    assert _generate_search_url(f"/{test_search_url_3}") == f"/{test_search_url_3}"
    assert _generate_search_url(f"{test_search_url_3}") == f"{test_search_url_3}"
    assert (
        _generate_search_url(f"{test_search_url_3}", default_count=5)
        == f"{test_search_url_3}&_count=5"
    )
    assert (
        _generate_search_url(f"{test_search_url_3}&_count=10", default_count=5)
        == f"{test_search_url_3}&_count=10"
    )
    assert (
        _generate_search_url(
            f"{test_search_url_3}&_count=10", default_since="2022-01-01T00:00:00"
        )
        == f"{test_search_url_3}"
        + f"{urllib.parse.quote('&_count=10&_since=2022-01-01T00:00:00', safe='?&=')}"
    )


@mock.patch("phdi.fhir.tabulation.tables._generate_search_url")
def test_generate_search_urls(patch_generate_search_url):
    patch_generate_search_url.side_effect = (
        lambda search, count, since: f"{search}||{count}||{since}"
    )

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.yaml"
        )
    )

    search_urls = _generate_search_urls(schema)

    assert search_urls == {
        "table 1A": "Patient||1000||2020-01-01T00:00:00",
        "table 2A": "Observation?category=laboratory||1000||None",
    }


def test_generate_search_urls_invalid():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "invalid_schema.yaml"
        )
    )

    with pytest.raises(ValueError):
        _generate_search_urls(schema)


def test_merge_include_query_params():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    table = schema.get("tables", {})["Physical Exams"]
    query_params = {"_include": "some-reference"}
    reference_locations = []

    for c in table.get("columns").values():
        if "reference_location" in c:
            reference_locations.append(c.get("reference_location"))
    for r in reference_locations:
        query_params = _merge_include_query_params_for_location(query_params, r)

    assert query_params == {
        "_include": ["some-reference", "Patient:general-practitioner"],
        "_revinclude": ["Observation:subject"],
    }


def test_merge_include_query_params_invalid():
    query_params = {"count": 1000}
    with pytest.raises(ValueError):
        _merge_include_query_params_for_location(query_params, "")


def test_drop_invalid():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.yaml"
        )
    )

    tabulated_data = {
        "table 1A": [
            ["Patient ID", "First Name", "Last Name", "Phone Number"],
            ["some-uuid", "John", "Doe", "123-456-7890"],
            ["some-uuid2", "First", "Last", "123-456-7890"],
        ],
        "table 2A": [
            ["Observation ID", "First Name", "Last Name", "Phone Number"],
            ["some-obsid", "John", "Doe", "123-456-7890"],
            ["some-obsid2", "First", "Last", "123-456-7890"],
        ],
    }

    # Keeps all resources because no invalid values
    table_name = "table 1A"
    no_invalid_values = drop_invalid(tabulated_data["table 1A"], schema, table_name)
    assert len(no_invalid_values) == 3
    assert no_invalid_values[1][3] == tabulated_data["table 1A"][1][3]

    # Drop null resource
    tabulated_data = {
        "table 1A": [
            ["Patient ID", "First Name", "Last Name", "Phone Number"],
            ["some-uuid", "John", "Doe", "123-456-7890"],
            ["some-uuid2", "First", "Last", "123-456-7890"],
        ],
        "table 2A": [
            ["Observation ID", "First Name", "Last Name", "Phone Number"],
            ["some-obsid", "John", "Doe", "123-456-7890"],
            ["some-obsid2", "First", "Last", None],
        ],
    }

    table_name = "table 2A"
    dropped_null_resource = drop_invalid(tabulated_data["table 2A"], schema, table_name)

    assert len(dropped_null_resource) == 2
    assert tabulated_data["table 2A"][1][0] == dropped_null_resource[1][0]

    # Empty strings are dropped
    tabulated_data = {
        "table 1A": [
            ["Patient ID", "First Name", "Last Name", "Phone Number"],
            ["some-uuid", "John", "Doe", "123-456-7890"],
            ["some-uuid2", "First", "Last", "123-456-7890"],
        ],
        "table 2A": [
            ["Observation ID", "First Name", "Last Name", "Phone Number"],
            ["some-obsid", "John", "Doe", "123-456-7890"],
            ["some-obsid2", "First", "Last", ""],
        ],
    }
    table_name = "table 2A"
    dropped_empty_string = drop_invalid(tabulated_data["table 2A"], schema, table_name)
    assert len(dropped_empty_string) == 2
    assert tabulated_data["table 2A"][1][0] == dropped_empty_string[1][0]

    # User-specified values are dropped
    tabulated_data = {
        "table 1A": [
            ["Patient ID", "First Name", "Last Name", "Phone Number"],
            ["some-uuid", "John", "Doe", "123-456-7890"],
            ["some-uuid2", "First", "Last", "123-456-7890"],
        ],
        "table 2A": [
            ["Observation ID", "First Name", "Last Name", "Phone Number"],
            ["some-obsid", "John", "Doe", "123-456-7890"],
            ["some-obsid2", "First", "Last", "Unknown"],
        ],
    }
    table_name = "table 2A"
    dropped_user_value = drop_invalid(tabulated_data["table 2A"], schema, table_name)
    assert len(dropped_user_value) == 2
    assert tabulated_data["table 2A"][1][0] == dropped_user_value[1][0]


@mock.patch("phdi.fhir.tabulation.tables.http_request_with_reauth")
def test_extract_data_from_fhir_search_incremental(patch_query):
    fhir_server_responses = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_query_response_200_example.json"
        )
    )
    mocked_http_response = mock.Mock(spec=Response)
    mocked_http_response.status_code = 200
    mocked_http_response._content = json.dumps(
        fhir_server_responses["content_1"]
    ).encode("utf-8")

    search_url = "http://some-fhir-url?some-query-url"
    search_url = "http://localhost:8080/fhir/Patient"
    cred_manager = None

    # Test that Next URL exists
    patch_query.return_value = mocked_http_response

    content, next_url = extract_data_from_fhir_search_incremental(
        search_url, cred_manager
    )

    assert next_url == fhir_server_responses.get("content_1").get("link")[0].get("url")
    assert content == fhir_server_responses.get("content_1").get("entry")

    # Test that Next URL is None
    mocked_http_response = mock.Mock(spec=Response)
    mocked_http_response.status_code = 200
    mocked_http_response._content = json.dumps(
        fhir_server_responses["content_2"]
    ).encode("utf-8")
    patch_query.return_value = mocked_http_response

    content, next_url = extract_data_from_fhir_search_incremental(
        search_url, cred_manager
    )

    assert next_url is None
    assert content == fhir_server_responses.get("content_2").get("entry")

    # Test that warning appears if no incremental data is returned
    mocked_http_response = mock.Mock(spec=Response)
    mocked_http_response.status_code = 200
    mocked_http_response._content = json.dumps("").encode("utf-8")
    patch_query.return_value = mocked_http_response

    with pytest.warns() as warn:
        content, next_url = extract_data_from_fhir_search_incremental(
            search_url, cred_manager
        )
    assert (
        "The search_url returned no incremental results: "
        + "http://localhost:8080/fhir/Patient"
    ) in str(warn[0].message)


@mock.patch("phdi.fhir.tabulation.tables.http_request_with_reauth")
def test_extract_data_from_fhir_search_incremental_auth(patch_query):
    """Test that the header of the request passed to http_request_with_reauth is set
    appropriately when a credential manager is provided and when one is not."""

    # Case 1: Credential manager is provided.
    cred_manager = mock.Mock()
    cred_manager.get_access_token.return_value = "my-access-token"
    search_url = "some-fhir-search-url"

    headers = {
        "Authorization": f"Bearer {cred_manager.get_access_token.return_value}",
        "Accept": "application/fhir+json",
        "Content-Type": "application/fhir+json",
    }

    mocked_http_response = mock.Mock(spec=Response)
    mocked_http_response.status_code = 200
    mocked_http_response._content = json.dumps("").encode("utf-8")
    patch_query.return_value = mocked_http_response

    extract_data_from_fhir_search_incremental(
        search_url=search_url, cred_manager=cred_manager
    )

    patch_query.assert_called_with(
        url=search_url,
        cred_manager=cred_manager,
        retry_count=2,
        request_type="GET",
        allowed_methods=["GET"],
        headers=headers,
    )

    cred_manager = None

    # Case 2: Credential manager is not provided.
    extract_data_from_fhir_search_incremental(
        search_url=search_url, cred_manager=cred_manager
    )

    patch_query.assert_called_with(
        url=search_url,
        cred_manager=cred_manager,
        retry_count=2,
        request_type="GET",
        allowed_methods=["GET"],
        headers={},
    )


@mock.patch("phdi.fhir.tabulation.tables.http_request_with_reauth")
def test_extract_data_from_fhir_search(patch_query):
    fhir_server_responses = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_query_response_200_example.json"
        )
    )

    search_url = "http://some-fhir-url?some-query-url"
    cred_manager = None

    # Test that Next URL exists
    mocked_http_response1 = mock.Mock(spec=Response)
    mocked_http_response1.status_code = 200
    mocked_http_response1._content = json.dumps(
        fhir_server_responses["content_1"]
    ).encode("utf-8")
    mocked_http_response2 = mock.Mock(spec=Response)
    mocked_http_response2.status_code = 200
    mocked_http_response2._content = json.dumps(
        fhir_server_responses["content_2"]
    ).encode("utf-8")

    patch_query.side_effect = [mocked_http_response1, mocked_http_response2]

    content = extract_data_from_fhir_search(search_url, cred_manager)

    expected_output = fhir_server_responses.get("content_1").get("entry")

    expected_output.extend(fhir_server_responses.get("content_2").get("entry"))

    assert content == expected_output


@mock.patch("phdi.fhir.tabulation.tables.extract_data_from_fhir_search_incremental")
def test_extract_data_from_fhir_search_no_data(patch_search):
    search_url = "http://some-fhir-url?some-query-url"
    cred_manager = None
    # Mock no results returned from incremental search
    patch_search.side_effect = [([], None)]
    with pytest.raises(ValueError) as e:
        extract_data_from_fhir_search(search_url, cred_manager)
    assert "No data returned from server with the following query" in str(e.value)


@mock.patch("phdi.fhir.tabulation.tables._generate_search_urls")
@mock.patch("phdi.fhir.tabulation.tables.extract_data_from_fhir_search")
def test_extract_data_from_schema(patch_search, patch_gen_urls):
    patch_gen_urls.return_value = {
        "Table 1A": "table_1a_search_string",
        "Table 2A": "table_2a_search_string",
    }

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.yaml"
        )
    )

    data = {
        "Table 1A": [
            {
                "resourceType": "Patient",
                "id": "pid1",
                "name": {"given": ["John"], "family": "Doe"},
            },
            {
                "resourceType": "Patient",
                "id": "pid1",
                "name": {"given": ["Jane"], "family": "Smith"},
            },
            {
                "resourceType": "Patient",
                "id": "pid1",
                "name": {"given": ["Pat"], "family": "Cranston"},
            },
        ],
        "Table 2A": [
            {"resourceType": "Observation", "id": "obs1", "subject": "pid1"},
            {"resourceType": "Observation", "id": "obs2", "subject": "pid1"},
            {"resourceType": "Observation", "id": "obs3", "subject": "pid2"},
        ],
    }

    # Mock data returned by search
    patch_search.side_effect = [
        data.get("Table 1A"),
        data.get("Table 2A"),
    ]

    fhir_url = "http://some-fhir-url?some-query-url"

    search_results = extract_data_from_schema(schema=schema, fhir_url=fhir_url)

    assert search_results == data

    patch_search.assert_has_calls(
        [
            mock.call(
                search_url=f"{fhir_url}/table_1a_search_string", cred_manager=None
            ),
            mock.call(
                search_url=f"{fhir_url}/table_2a_search_string", cred_manager=None
            ),
        ]
    )


@mock.patch("phdi.fhir.tabulation.tables.extract_data_from_fhir_search_incremental")
def test_generate_tables(patch_search_incremental):
    # Set up
    schema_path = (
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "tabulation"
        / "tabulation_schema.yaml"
    )

    output_params = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema_output_data.json"
        )
    )
    fhir_url = "https://some_fhir_server_url"
    cred_manager = None

    mock_extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    mock_next_url = None

    # Mocks for extract_data_from_schema
    patch_search_incremental.return_value = (
        mock_extracted_data["entry"],
        mock_next_url,
    )

    generate_tables(
        schema_path=schema_path,
        output_params=output_params,
        fhir_url=fhir_url,
        cred_manager=cred_manager,
    )

    patch_search_incremental.assert_called()

    patients_path = os.path.join(
        output_params["Patients"]["directory"], output_params["Patients"]["filename"]
    )
    # Test that file was created
    assert os.path.exists(patients_path) is True

    # Test that file content match expected content
    with open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulated_patients.csv"
        ),
        "r",
    ) as e:
        csvreader = csv.reader(e)
        expected_content = [row for row in csvreader]

    with open(patients_path, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        line = 0
        for row in reader:
            for i in range(len(row)):
                assert row[i] == str(expected_content[line][i])
            line += 1
        assert line == 4

    # Remove file after testing is complete
    if os.path.isfile(patients_path):  # pragma: no cover
        os.remove(patients_path)

    physical_exams_path = os.path.join(
        output_params["Physical Exams"]["directory"],
        output_params["Physical Exams"]["filename"],
    )
    # Test that file was created
    assert os.path.exists(physical_exams_path) is True

    # Test that file content match expected content
    with open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation"
            / "tabulated_physical_exam.csv"
        ),
        "r",
    ) as e:
        csvreader = csv.reader(e)
        expected_content = [row for row in csvreader]

    with open(physical_exams_path, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        line = 0
        for row in reader:
            for i in range(len(row)):
                assert row[i] == str(expected_content[line][i])
            line += 1
        assert line == 4

    # Remove file after testing is complete
    if os.path.isfile(physical_exams_path):  # pragma: no cover
        os.remove(physical_exams_path)
