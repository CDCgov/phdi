from copy import deepcopy
from unittest import mock

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def fhir_bundle(read_json_from_phdi_test_assets):
    return read_json_from_phdi_test_assets("patient_bundle.json")


@pytest.fixture
def fhir_bundle_w_float(read_json_from_phdi_test_assets):
    return read_json_from_phdi_test_assets("patient_bundle_w_floats.json")


@pytest.fixture
def test_schema(read_schema_from_default_schemas):
    return read_schema_from_default_schemas("test_schema.json")


@pytest.fixture
def reference_bundle(read_json_from_phdi_test_assets):
    return read_json_from_phdi_test_assets("patient_bundle_w_labs.json")


@pytest.fixture
def test_reference_schema(read_schema_from_default_schemas):
    return read_schema_from_default_schemas("test_reference_schema.json")


expected_successful_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": "John ",
        "last_name": "doe",
        "latitude": None,
        "longitude": None,
        "active_problems": [],
    },
}

expected_successful_response_with_meta_data = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": {
            "value": "John ",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name"
            + ".first().given.first()",
            "data_type": "string",
            "resource_type": "Patient",
            "category": "name",
        },
        "last_name": {
            "value": "doe",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name"
            + ".first().family",
            "data_type": "string",
            "resource_type": "Patient",
        },
        "latitude": {
            "value": None,
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient')"
            + ".address.extension.where"
            + "(url='http://hl7.org/fhir/StructureDefinition/geolocation').extension."
            + "where(url='latitude').valueDecimal",
            "data_type": "float",
            "resource_type": "Patient",
        },
        "longitude": {
            "value": None,
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').address"
            + ".extension.where"
            + "(url='http://hl7.org/fhir/StructureDefinition/geolocation').extension"
            + ".where(url='longitude').valueDecimal",
            "data_type": "float",
            "resource_type": "Patient",
        },
        "active_problems": {
            "value": [],
            "fhir_path": "Bundle.entry.resource.where(resourceType='Condition')"
            + ".where(category.coding.code='problem-item-list')",
            "data_type": "array",
            "resource_type": "Condition",
        },
    },
}

expected_successful_response_floats = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": "John ",
        "last_name": "doe",
        "latitude": "34.58002",
        "longitude": "-118.08925",
        "active_problems": [],
    },
}

expected_successful_response_floats_with_meta_data = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": {
            "value": "John ",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name"
            + ".first().given.first()",
            "data_type": "string",
            "resource_type": "Patient",
            "category": "name",
        },
        "last_name": {
            "value": "doe",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name"
            + ".first().family",
            "data_type": "string",
            "resource_type": "Patient",
        },
        "latitude": {
            "value": "34.58002",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').address"
            + ".extension"
            + ".where(url='http://hl7.org/fhir/StructureDefinition/geolocation')"
            + ".extension.where(url='latitude').valueDecimal",
            "data_type": "float",
            "resource_type": "Patient",
        },
        "longitude": {
            "value": "-118.08925",
            "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').address"
            + ".extension"
            + ".where(url='http://hl7.org/fhir/StructureDefinition/geolocation')"
            + ".extension.where(url='longitude').valueDecimal",
            "data_type": "float",
            "resource_type": "Patient",
        },
        "active_problems": {
            "value": [],
            "fhir_path": "Bundle.entry.resource.where(resourceType='Condition')"
            + ".where(category.coding.code='problem-item-list')",
            "data_type": "array",
            "resource_type": "Condition",
        },
    },
}


expected_reference_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": "John ",
        "last_name": "doe",
        "labs": [
            {
                "test_type": "Blood culture",
                "test_result_code_display": "Staphylococcus aureus",
                "ordering_provider": "Western Pennsylvania Medical General",
                "requesting_organization_contact_person": "Dr. Totally Real Doctor, M.D.",  # noqa
            }
        ],
    },
}


def test_parse_message_success_internal_schema(fhir_bundle, fhir_bundle_w_float):
    test_request = {
        "message_format": "fhir",
        "parsing_schema_name": "test_schema.json",
        "message": fhir_bundle,
    }

    actual_response = client.post("/parse_message", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response

    test_request2 = {
        "message_format": "fhir",
        "parsing_schema_name": "test_schema.json",
        "message": fhir_bundle_w_float,
    }

    actual_response2 = client.post("/parse_message", json=test_request2)
    assert actual_response2.status_code == 200
    assert actual_response2.json() == expected_successful_response_floats


def test_parse_message_success_internal_schema_with_metadata(
    fhir_bundle,
    fhir_bundle_w_float,
):
    test_request = {
        "message_format": "fhir",
        "parsing_schema_name": "test_schema.json",
        "include_metadata": "true",
        "message": fhir_bundle,
    }

    actual_response = client.post("/parse_message", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response_with_meta_data

    test_request2 = {
        "message_format": "fhir",
        "include_metadata": "true",
        "parsing_schema_name": "test_schema.json",
        "message": fhir_bundle_w_float,
    }

    actual_response2 = client.post("/parse_message", json=test_request2)
    assert actual_response2.status_code == 200
    assert actual_response2.json() == expected_successful_response_floats_with_meta_data


def test_parse_message_success_external_schema(test_schema, fhir_bundle):
    request = {
        "message_format": "fhir",
        "parsing_schema": test_schema,
        "message": fhir_bundle,
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response


def test_parse_message_success_referenced_resources(
    test_reference_schema, reference_bundle
):
    request = {
        "message_format": "fhir",
        "parsing_schema": test_reference_schema,
        "message": reference_bundle,
    }
    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_reference_response


@mock.patch("app.main.convert_to_fhir")
@mock.patch("app.main.get_credential_manager")
def test_parse_message_success_non_fhir(
    patched_get_credential_manager, patched_convert_to_fhir, fhir_bundle
):
    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "test_schema.json",
        "fhir_converter_url": "some-url",
        "credential_manager": "azure",
        "message": "some-hl7v2-elr-message",
    }

    patched_get_credential_manager.return_value = "some-credential-manager"
    convert_to_fhir_response = mock.Mock()
    convert_to_fhir_response.status_code = 200
    convert_to_fhir_response.json.return_value = {"FhirResource": fhir_bundle}
    patched_convert_to_fhir.return_value = convert_to_fhir_response

    actual_response = client.post("/parse_message", json=request)

    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response
    patched_convert_to_fhir.assert_called_with(
        message="some-hl7v2-elr-message",
        message_type="elr",
        fhir_converter_url="some-url",
        credential_manager="some-credential-manager",
    )
    patched_get_credential_manager.assert_called_with(
        credential_manager="azure", location_url="some-url"
    )


def test_parse_message_non_fhir_missing_converter_url():
    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "test_schema.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "message": "The following values are required, but were not included in the "
        "request and could not be read from the environment. Please resubmit the "
        "request including these values or add them as environment variables to this "
        "service. missing values: fhir_converter_url.",
        "parsed_values": {},
    }


@mock.patch("app.main.convert_to_fhir")
def test_parse_message_fhir_conversion_fail(patched_convert_to_fhir):
    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "test_schema.json",
        "fhir_converter_url": "some-url",
        "message": "some-hl7v2-elr-message",
    }

    convert_to_fhir_response = mock.Mock()
    convert_to_fhir_response.status_code = 400
    convert_to_fhir_response.text = "some error message returned by the FHIR converter"
    patched_convert_to_fhir.return_value = convert_to_fhir_response
    expected_response = {
        "message": f"Failed to convert to FHIR: {convert_to_fhir_response.text}",
        "parsed_values": {},
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == expected_response
    patched_convert_to_fhir.assert_called_with(
        message="some-hl7v2-elr-message",
        message_type="elr",
        fhir_converter_url="some-url",
        credential_manager=None,
    )


def test_parse_message_non_fhir_missing_message_type():
    request = {
        "message_format": "hl7v2",
        "parsing_schema_name": "test_schema.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "When the message format is not FHIR then the message type must be included."
    )


def test_parse_message_internal_and_external_schema(test_reference_schema):
    request = {
        "message_format": "fhir",
        "parsing_schema": test_reference_schema,
        "parsing_schema_name": "test_schema.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for both 'parsing_schema' and 'parsing_schema_name' have been "
        "provided. Only one of these values is permited."
    )


def test_parse_message_neither_internal_nor_external_schema():
    request = {
        "message_format": "fhir",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for 'parsing_schema' and 'parsing_schema_name' have not been "
        "provided. One, but not both, of these values is required."
    )


def test_schema_without_reference_lookup(test_reference_schema):
    no_lookup_schema = deepcopy(test_reference_schema)
    del no_lookup_schema["labs"]["secondary_schema"]["ordering_provider"][
        "reference_lookup"
    ]
    request = {
        "message_format": "fhir",
        "message": {},
        "parsing_schema": no_lookup_schema,
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Secondary fields in the parsing schema that reference other "
        "resources must include a `reference_lookup` field that identifies "
        "where the reference ID can be found."
    )


def test_schema_without_identifier_path(test_reference_schema):
    no_bundle_schema = deepcopy(test_reference_schema)
    no_bundle_schema["labs"]["secondary_schema"]["ordering_provider"]["fhir_path"] = (
        "Observation.provider"
    )
    request = {
        "message_format": "fhir",
        "message": {},
        "parsing_schema": no_bundle_schema,
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Secondary fields in the parsing schema that provide `reference_lookup` "
        "locations must have a `fhir_path` that begins with `Bundle` and identifies "
        "the type of resource being referenced."
    )
