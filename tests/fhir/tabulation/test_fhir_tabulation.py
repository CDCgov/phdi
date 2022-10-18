import json
import pathlib
import yaml

from unittest import mock

from phdi.fhir.tabulation.tables import (
    _apply_selection_criteria,
    apply_schema_to_resource,
    drop_null,
    generate_all_tables_in_schema,
    generate_table,
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
        ["some-uuid2", "Marcelle", "Goggins", ""],
    ]

    responses_1_null = drop_null(
        fhir_server_responses_1_null, schema["my_table"]["Patient"]
    )
    assert len(responses_1_null) == 2
    assert responses_1_null[1][0] == fhir_server_responses_1_null[1][0]
