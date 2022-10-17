import json
import pathlib
import urllib.parse
import yaml

from unittest import mock

from phdi.fhir.tabulation.tables import (
    _apply_selection_criteria,
    _generate_search_url,
    apply_schema_to_resource,
    generate_all_tables_in_schema,
    generate_table,
    tabulate_data,
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

    # Test for inserting empty string if field not found
    del resource["name"][0]["family"]
    assert apply_schema_to_resource(resource, schema) == {
        "patient_id": "some-uuid",
        "first_name": "John ",
        "last_name": "",
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


def test_tabulate_data():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "test_schema.yaml"
        )
    )
    schema = schema["my_table"]
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )

    tabulated_data = tabulate_data(extracted_data, schema)

    # Check all columns from schema present
    assert tabulated_data[0] == [
        "first_name",
        "last_name",
        "patient_id",
        "phone_number",
    ]

    # Check all records in data bundle present
    assert len(extracted_data["entry"]) + 1 == len(tabulated_data)

    # Check for expected blank strings
    assert tabulated_data[3][1] == ""
    assert tabulated_data[2][3] == ""

    # Verify full row is correctly tabulated
    assert tabulated_data[1] == [
        "Kimberley248",
        "Price929",
        "907844f6-7c99-eabc-f68e-d92189729a55",
        "555-690-3898",
    ]


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
        "Patient?birtdate=2000-01-01T00:00:00", safe="/?="
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
