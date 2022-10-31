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
    tabulate_data,
    _get_reference_directions,
    _build_reference_dicts,
    _generate_search_url,
    _generate_search_urls,
    _dereference_included_resource,
    extract_data_from_fhir_search_incremental,
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
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

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

    # Test for no schema in yaml file that matches incoming
    # resource type
    resource = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    resource = resource["entry"][0]["resource"]
    assert apply_schema_to_resource(resource, schema) == {}

    # Test for raised exception if no resource type at all
    del schema["tables"]["table 1A"]["resource_type"]
    with pytest.raises(
        ValueError,
        match="Each table must specify resource_type. resource_type not found in table table 1A.",  # noqa
    ):
        apply_schema_to_resource(resource, schema)


def test_tabulate_data():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )

    tabulated_data = tabulate_data(extracted_data, schema)

    assert set(tabulated_data.keys()) == {"Patients", "Physical Exams"}

    # Check all columns from schema present
    assert set(tabulated_data["Patients"][0]) == {
        "Patient ID",
        "First Name",
        "Last Name",
        "Phone Number",
    }
    assert set(tabulated_data["Physical Exams"][0]) == {
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
        },
        {"65489-asdf5-6d8w2-zz5g8", "John", "Shepard", None},
        {"some-uuid", "John ", None, "123-456-7890"},
    ]
    assert len(tabulated_data["Patients"][1:]) == 3
    tests_run = 0
    for row in row_sets:
        found_match = False
        for table_row in tabulated_data["Patients"][1:]:
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
        ["no-srsly-i-am-hoomun", "Zakera Ward", "Shepard", None],
        ["Faketon", None, None, ["obs2", "obs3"]],
    ]
    assert len(tabulated_data["Physical Exams"][1:]) == 3
    tests_run = 0
    for row in row_lists:
        found_match = False
        for table_row in tabulated_data["Physical Exams"][1:]:
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


@mock.patch("phdi.fhir.tabulation.tables.write_table")
@mock.patch("phdi.fhir.tabulation.tables.fhir_server_get")
def test_generate_table_success(patch_query, patch_write):

    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

    # This test only uses patient resources
    del schema.get("tables")["table 2A"]

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
        schema,
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
                schema,
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
                schema,
            )
        ],
        output_path,
        output_format,
        patch_write(
            (
                [
                    apply_schema_to_resource(
                        fhir_server_responses["content_1"]["entry"][0]["resource"],
                        schema,
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
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

    # This test only uses patient resources
    del schema.get("tables")["table 2A"]

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
            pathlib.Path(__file__).parent.parent.parent / "assets" / "valid_schema.yaml"
        )
    )

    # This test only uses patient resources
    del schema.get("tables")["table 2A"]

    patched_load_schema.return_value = schema

    generate_all_tables_in_schema(
        schema_path, output_path, output_format, fhir_url, mock_cred_manager
    )

    patched_make_table.assert_called_with(
        schema,
        output_path,
        output_format,
        fhir_url,
        mock_cred_manager,
    )


def test_get_reference_directions():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
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
            / "tabulation_schema.yaml"
        )
    )
    ref_directions = _get_reference_directions(schema)

    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    ref_dicts = _build_reference_dicts(extracted_data, ref_directions)
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
            / "tabulation_schema.yaml"
        )
    )
    data = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    ref_directions = _get_reference_directions(schema)
    ref_dicts = _build_reference_dicts(data, ref_directions)

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
