import json
import pathlib
import pytest
import urllib.parse
import yaml

from unittest import mock

from phdi.fhir.tabulation.tables import (
    _apply_selection_criteria,
    apply_schema_to_resource,
    drop_null,
    generate_all_tables_in_schema,
    generate_table,
    _generate_search_url,
    _generate_search_urls,
    extract_data_from_fhir_search_incremental,
    extract_data_from_fhir_search,
    extract_data_from_fhir_schema,
)


def test_apply_selection_criteria():
    selection_criteria_test_list = ["one", "two", "three"]
    assert _apply_selection_criteria(selection_criteria_test_list, "first") == "one"
    assert _apply_selection_criteria(selection_criteria_test_list, "last") == "three"
    assert (
        _apply_selection_criteria(selection_criteria_test_list, "random")
        in selection_criteria_test_list
    )
    assert _apply_selection_criteria(selection_criteria_test_list, "all") == ",".join(
        selection_criteria_test_list
    )


def test_apply_schema_to_resource():
    resource = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )

    resource = resource["entry"][1]["resource"]

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )
    schema = schema["my_table"]

    assert apply_schema_to_resource(resource, schema) == {
        "patient_id": "some-uuid",
        "first_name": "John ",
        "last_name": "doe",
        "phone_number": "123-456-7890",
    }

    # Test for resource_schema is None
    resource = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    resource = resource["entry"][0]["resource"]
    assert apply_schema_to_resource(resource, schema) == {}


@mock.patch("phdi.fhir.tabulation.tables.write_table")
@mock.patch("phdi.fhir.tabulation.tables.fhir_server_get")
def test_generate_table_success(patch_query, patch_write):

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )

    output_path = mock.Mock()
    output_path.__truediv__ = (  # Redefine division operator to prevent failure.
        lambda x, y: x
    )
    output_format = "parquet"
    fhir_url = "https://some_fhir_server_url"
    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    fhir_server_responses = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_query_response_200_example.json"
        )
    )

    query_response_1 = mock.Mock()
    query_response_1.status_code = fhir_server_responses["status_code_1"]
    query_response_1.content = json.dumps(fhir_server_responses["content_1"])

    query_response_2 = mock.Mock()
    query_response_2.status_code = fhir_server_responses["status_code_2"]
    query_response_2.content = json.dumps(fhir_server_responses["content_2"])

    patch_query.side_effect = [query_response_1, query_response_2]

    generate_table(
        schema["my_table"],
        output_path,
        output_format,
        fhir_url,
        mock_cred_manager,
    )

    assert len(patch_write.call_args_list[0]) == 2

    assert patch_write.call_args_list[0][0] == (
        [
            apply_schema_to_resource(
                fhir_server_responses["content_1"]["entry"][0]["resource"],
                schema["my_table"],
            )
        ],
        output_path,
        output_format,
        None,
    )
    assert patch_write.call_args_list[1][0] == (
        [
            apply_schema_to_resource(
                fhir_server_responses["content_2"]["entry"][0]["resource"],
                schema["my_table"],
            )
        ],
        output_path,
        output_format,
        patch_write(
            (
                [
                    apply_schema_to_resource(
                        fhir_server_responses["content_1"]["entry"][0]["resource"],
                        schema["my_table"],
                    )
                ],
                output_path,
                output_format,
                None,
            )
        ),
    )


@mock.patch("phdi.fhir.tabulation.tables.write_table")
@mock.patch("phdi.fhir.tabulation.tables.fhir_server_get")
def test_generate_table_fail(patch_query, patch_write):

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )

    output_path = mock.Mock()
    output_path.__truediv__ = (  # Redefine division operator to prevent failure.
        lambda x, y: x
    )

    output_format = "parquet"

    fhir_url = "https://some_fhir_server_url"
    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    response = mock.Mock(status_code=400)
    patch_query.return_value = response

    generate_table(
        schema,
        output_path,
        output_format,
        fhir_url,
        mock_cred_manager,
    )

    patch_query.assert_called()
    patch_write.assert_not_called()


@mock.patch("phdi.fhir.tabulation.tables.generate_table")
@mock.patch("phdi.fhir.tabulation.tables.load_schema")
def test_generate_all_tables_schema(patched_load_schema, patched_make_table):

    schema_path = mock.Mock()
    output_path = mock.Mock()
    output_path.__truediv__ = (  # Redefine division operator to prevent failure.
        lambda x, y: x
    )
    output_format = "parquet"
    fhir_url = "https://some_fhir_url"
    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )

    patched_load_schema.return_value = schema

    generate_all_tables_in_schema(
        schema_path, output_path, output_format, fhir_url, mock_cred_manager
    )

    patched_make_table.assert_called_with(
        schema["my_table"],
        output_path,
        output_format,
        fhir_url,
        mock_cred_manager,
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
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

    search_urls = _generate_search_urls(schema)

    assert search_urls == {
        "table 1A": "Patient||1000||2020-01-01T00:00:00",
        "table 2A": "Observation?category="
        + urllib.parse.quote(
            "http://hl7.org/fhir/ValueSet/observation-category|laboratory", safe=""
        )
        + urllib.parse.quote("||1000||None", safe="|"),
    }


def test_generate_search_urls_invalid():

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "invalid_schema.yaml"
        )
    )

    with pytest.raises(ValueError):
        _generate_search_urls(schema)


def test_drop_null():

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )

    fhir_server_responses_no_nulls = [
        ["patient_id", "first_name", "last_name", "phone_number"],
        ["some-uuid", "John", "Doe", "123-456-7890"],
        ["some-uuid2", "First", "Last", "123-456-7890"],
    ]

    # Keeps all resources because include_nulls all False
    responses_no_nulls = drop_null(
        fhir_server_responses_no_nulls, schema["my_table"]["Patient"]
    )
    assert len(responses_no_nulls) == 3
    assert responses_no_nulls[1][3] == fhir_server_responses_no_nulls[1][3]

    # Drop null resource
    fhir_server_responses_1_null = [
        ["patient_id", "first_name", "last_name", "phone_number"],
        ["some-uuid", "John", "Doe", "123-456-7890"],
        ["some-uuid2", "Firstname", "Lastname", ""],
    ]

    responses_1_null = drop_null(
        fhir_server_responses_1_null, schema["my_table"]["Patient"]
    )
    assert len(responses_1_null) == 2
    assert responses_1_null[1][0] == fhir_server_responses_1_null[1][0]


@mock.patch("phdi.fhir.tabulation.tables.http_request_with_reauth")
def test_extract_data_from_fhir_search_incremental(patch_query):

    fhir_server_responses = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_query_response_200_example.json"
        )
    )

    search_url = "http://some-fhir-url?some-query-url"
    cred_manager = None

    # Test that Next URL exists
    patch_query.return_value = fhir_server_responses.get("content_1")

    content, next_url = extract_data_from_fhir_search_incremental(
        search_url, cred_manager
    )

    assert next_url == fhir_server_responses.get("content_1").get("link")[0].get("url")
    assert content == [
        entry_json.get("resource")
        for entry_json in fhir_server_responses.get("content_1").get("entry")
    ]

    # Test that Next URL is None
    patch_query.return_value = fhir_server_responses["content_2"]

    content, next_url = extract_data_from_fhir_search_incremental(
        search_url, cred_manager
    )

    assert next_url is None
    assert content == [
        entry_json.get("resource")
        for entry_json in fhir_server_responses.get("content_2").get("entry")
    ]


@mock.patch("phdi.fhir.tabulation.tables.http_request_with_reauth")
def test_extract_data_from_fhir_search(patch_query):

    fhir_server_responses = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_query_response_200_example.json"
        )
    )

    search_url = "http://some-fhir-url?some-query-url"
    cred_manager = None

    # Test that Next URL exists
    patch_query.side_effect = [
        fhir_server_responses.get("content_1"),
        fhir_server_responses.get("content_2"),
    ]

    content = extract_data_from_fhir_search(search_url, cred_manager)

    expected_output = [
        entry_json.get("resource")
        for entry_json in fhir_server_responses.get("content_1").get("entry")
    ]
    expected_output.extend(
        [
            entry_json.get("resource")
            for entry_json in fhir_server_responses.get("content_2").get("entry")
        ]
    )

    assert content == expected_output


@mock.patch("phdi.fhir.tabulation.tables._generate_search_urls")
@mock.patch("phdi.fhir.tabulation.tables.extract_data_from_fhir_search")
def test_extract_data_from_fhir_schema(patch_search, patch_gen_urls):
    patch_gen_urls.return_value = {
        "Table 1A": "table_1a_search_string",
        "Table 2A": "table_2a_search_string",
    }

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

    data = {
        "Table 1A": [
            ["Patient ID", "First Name", "Last Name", "Phone Number"],
            ["pid1", "John", "Doe", "111-222-3333"],
            ["pid2", "Jane", "Smith", "111-222-4444"],
            ["pid3", "Pat", "Cranston", "111-222-5555"],
        ],
        "Table 2A": [
            ["Observation ID", "Observation Subject"],
            ["oid1", "Patient/pid1"],
            ["oid2", "Patient/pid1"],
            ["oid3", "Patient/pid2"],
        ],
    }

    # Mock data returned by search
    patch_search.side_effect = [
        data.get("Table 1A"),
        data.get("Table 2A"),
    ]

    fhir_url = "http://some-fhir-url?some-query-url"

    search_results = extract_data_from_fhir_schema(schema=schema, fhir_url=fhir_url)

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
