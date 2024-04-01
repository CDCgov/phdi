# flake8: noqa
import json
from unittest import mock

import pytest
from app.main import app
from app.service import add_data_source_to_bundle
from app.service import resolve_references
from fastapi.testclient import TestClient
from lxml import etree

client = TestClient(app)

valid_request = {
    "input_data": "VALID_INPUT_DATA",
    "input_type": "elr",
    "root_template": "ADT_A01",
}

valid_request_with_rr = {
    "input_data": "VALID_INPUT_DATA",
    "input_type": "ecr",
    "root_template": "EICR",
    "rr_data": "RR",
}

global valid_response
valid_response = {
    "Status": "OK",
    "FhirResource": {
        "resourceType": "Bundle",
        "type": "batch",
        "timestamp": "2021-08-18T11:26:00+02:15",
        "identifier": {"value": "MSG00001"},
        "id": "513a3d06-5e87-6fbc-ad1b-170ab430499f",
        "entry": [
            {
                "fullUrl": "urn:uuid:02710678-32ab-4cea-b2f3-859b40a93ce3",
                "resource": {
                    "resourceType": "Patient",
                    "id": "02710678-32ab-4cea-b2f3-859b40a93ce3",
                },
            }
        ],
    },
}
conversion_failure_response = {
    "_mock_call_args": None,
    "_mock_call_args_list": [],
    "_mock_call_count": 0,
    "_mock_called": False,
    "_mock_children": {},
    "_mock_delegate": None,
    "_mock_methods": None,
    "_mock_mock_calls": [],
    "_mock_name": None,
    "_mock_new_name": "()",
    "_mock_new_parent": {},
    "_mock_parent": None,
    "_mock_return_value": {"name": "DEFAULT"},
    "_mock_sealed": False,
    "_mock_side_effect": None,
    "_mock_unsafe": False,
    "_mock_wraps": None,
    "_spec_asyncs": [],
    "_spec_class": None,
    "_spec_set": None,
    "_spec_signature": None,
    "method_calls": [],
    "fhir_conversion_failed": "true",
    "returncode": 1,
}

missing_input_data_request = {"input_type": "elr", "root_template": "ADT_A01"}

missing_input_data_response = {
    "detail": [
        {
            "loc": ["body", "input_data"],
            "msg": "field required",
            "type": "value_error.missing",
        }
    ]
}

invalid_input_type_request = {
    "input_data": "VALID_INPUT_DATA",
    "input_type": "hl7v3",
    "root_template": "ADT_A01",
}

invalid_input_type_response = {
    "detail": [
        {
            "loc": ["body", "input_type"],
            "msg": "value is not a valid enumeration member; permitted: 'elr', 'vxu', 'ecr'",
            "type": "type_error.enum",
            "ctx": {"enum_values": ["elr", "vxu", "ecr"]},
        }
    ]
}

invalid_root_template_request = {
    "input_data": "VALID_INPUT_DATA",
    "input_type": "elr",
    "root_template": "INVALID_ROOT_TEMPLATE",
}

invalid_root_template_response = {
    "detail": [
        {
            "loc": ["body", "root_template"],
            "msg": "value is not a valid enumeration member; permitted: 'ADT_A01', 'ADT_A02', 'ADT_A03', 'ADT_A04', 'ADT_A05', 'ADT_A06', 'ADT_A07', 'ADT_A08', 'ADT_A09', 'ADT_A10', 'ADT_A11', 'ADT_A13', 'ADT_A14', 'ADT_A15', 'ADT_A16', 'ADT_A25', 'ADT_A26', 'ADT_A27', 'ADT_A28', 'ADT_A29', 'ADT_A31', 'ADT_A40', 'ADT_A41', 'ADT_A45', 'ADT_A47', 'ADT_A60', 'BAR_P01', 'BAR_P02', 'BAR_P12', 'DFT_P03', 'DFT_P11', 'MDM_T01', 'MDM_T02', 'MDM_T05', 'MDM_T06', 'MDM_T09', 'MDM_T10', 'OMG_O19', 'OML_O21', 'ORM_O01', 'ORU_R01', 'OUL_R22', 'OUL_R23', 'OUL_R24', 'RDE_O11', 'RDE_O25', 'RDS_O13', 'REF_I12', 'REF_I14', 'SIU_S12', 'SIU_S13', 'SIU_S14', 'SIU_S15', 'SIU_S16', 'SIU_S17', 'SIU_S26', 'VXU_V04', 'CCD', 'EICR', 'ELR', 'ConsultationNote', 'DischargeSummary', 'Header', 'HistoryandPhysical', 'OperativeNote', 'ProcedureNote', 'ProgressNote', 'ReferralNote', 'TransferSummary'",
            "type": "type_error.enum",
            "ctx": {
                "enum_values": [
                    "ADT_A01",
                    "ADT_A02",
                    "ADT_A03",
                    "ADT_A04",
                    "ADT_A05",
                    "ADT_A06",
                    "ADT_A07",
                    "ADT_A08",
                    "ADT_A09",
                    "ADT_A10",
                    "ADT_A11",
                    "ADT_A13",
                    "ADT_A14",
                    "ADT_A15",
                    "ADT_A16",
                    "ADT_A25",
                    "ADT_A26",
                    "ADT_A27",
                    "ADT_A28",
                    "ADT_A29",
                    "ADT_A31",
                    "ADT_A40",
                    "ADT_A41",
                    "ADT_A45",
                    "ADT_A47",
                    "ADT_A60",
                    "BAR_P01",
                    "BAR_P02",
                    "BAR_P12",
                    "DFT_P03",
                    "DFT_P11",
                    "MDM_T01",
                    "MDM_T02",
                    "MDM_T05",
                    "MDM_T06",
                    "MDM_T09",
                    "MDM_T10",
                    "OMG_O19",
                    "OML_O21",
                    "ORM_O01",
                    "ORU_R01",
                    "OUL_R22",
                    "OUL_R23",
                    "OUL_R24",
                    "RDE_O11",
                    "RDE_O25",
                    "RDS_O13",
                    "REF_I12",
                    "REF_I14",
                    "SIU_S12",
                    "SIU_S13",
                    "SIU_S14",
                    "SIU_S15",
                    "SIU_S16",
                    "SIU_S17",
                    "SIU_S26",
                    "VXU_V04",
                    "CCD",
                    "EICR",
                    "ELR",
                    "ConsultationNote",
                    "DischargeSummary",
                    "Header",
                    "HistoryandPhysical",
                    "OperativeNote",
                    "ProcedureNote",
                    "ProgressNote",
                    "ReferralNote",
                    "TransferSummary",
                ]
            },
        }
    ]
}

invalid_rr_data_request = {
    "input_data": "<VALID_INPUT_DATA />",
    "input_type": "vxu",
    "root_template": "EICR",
    "rr_data": "RR",
}

invalid_rr_data_response = {
    "message": "Reportability Response (RR) data is only accepted for eCR "
    "conversion requests."
}


@mock.patch("app.service.json.load")
@mock.patch("app.service.open")
@mock.patch("app.service.subprocess.run")
@mock.patch("app.service.Path")
@mock.patch("app.main.resolve_references")
def test_convert_valid_request(
    patched_resolve_references,
    patched_file_path,
    patched_subprocess_run,
    patched_open,
    patched_json_load,
):
    global valid_response
    patched_subprocess_run.return_value = mock.Mock(returncode=0)
    patched_json_load.return_value = valid_response
    patched_file_path = mock.Mock()
    actual_response = client.post(
        "/convert-to-fhir",
        json=valid_request,
    )
    assert actual_response.status_code == 200
    actual_response = actual_response.json().get("response")
    new_id = actual_response["FhirResource"]["entry"][0]["resource"]["id"]
    old_id = valid_response["FhirResource"]["entry"][0]["resource"]["id"]
    valid_response = json.dumps(valid_response)
    valid_response = valid_response.replace(old_id, new_id)
    valid_response = json.loads(valid_response)
    add_data_source_to_bundle(valid_response["FhirResource"], "elr")
    assert actual_response == valid_response


@mock.patch("app.service.json.load")
@mock.patch("app.service.open")
@mock.patch("app.service.subprocess.run")
@mock.patch("app.service.Path")
@mock.patch("app.main.add_rr_data_to_eicr")
@mock.patch("app.main.resolve_references")
def test_convert_valid_request_with_rr_data(
    patched_resolve_references,
    patched_add_rr_data_to_eicr,
    patched_file_path,
    patched_subprocess_run,
    patched_open,
    patched_json_load,
):
    patched_subprocess_run.return_value = mock.Mock(returncode=0)
    patched_json_load.return_value = valid_response
    patched_file_path = mock.Mock()
    patched_add_rr_data_to_eicr.return_value = "VALID_INPUT_DATA + RR"
    actual_response = client.post(
        "/convert-to-fhir",
        json=valid_request_with_rr,
    )
    assert actual_response.status_code == 200


@mock.patch("app.service.json.load")
@mock.patch("app.service.open")
@mock.patch("app.service.subprocess.run")
@mock.patch("app.service.Path")
@mock.patch("app.main.resolve_references")
def test_convert_conversion_failure(
    patched_resolve_references,
    patched_file_path,
    patched_subprocess_run,
    patched_open,
    patched_json_load,
):
    patched_subprocess_run.return_value = mock.Mock(returncode=1)
    patched_json_load.return_value = valid_response
    patched_file_path = mock.Mock()

    actual_response = client.post(
        "/convert-to-fhir",
        json=valid_request,
    )
    assert actual_response.status_code == 400
    assert actual_response.json().get("response") == conversion_failure_response


@mock.patch("app.service.subprocess.run")
def test_convert_missing_input_data(patched_subprocess_run):
    patched_subprocess_run.return_value = mock.Mock(returncode=1)
    actual_response = client.post(
        "/convert-to-fhir",
        json=missing_input_data_request,
    )
    assert actual_response.status_code == 422
    assert actual_response.json() == missing_input_data_response


@mock.patch("app.service.subprocess.run")
def test_convert_invalid_input_type(patched_subprocess_run):
    patched_subprocess_run.return_value = mock.Mock(returncode=1)
    actual_response = client.post(
        "/convert-to-fhir",
        json=invalid_input_type_request,
    )
    assert actual_response.status_code == 422
    assert actual_response.json() == invalid_input_type_response


@mock.patch("app.service.subprocess.run")
def test_convert_invalid_root_template(patched_subprocess_run):
    patched_subprocess_run.return_value = mock.Mock(returncode=1)
    actual_response = client.post(
        "/convert-to-fhir",
        json=invalid_root_template_request,
    )
    assert actual_response.status_code == 422
    assert actual_response.json() == invalid_root_template_response


def test_conversion_fails_with_invalid_rr_request():
    actual_response = client.post(
        "/convert-to-fhir",
        json=invalid_rr_data_request,
    )
    assert actual_response.status_code == 422
    assert actual_response.json() == invalid_rr_data_response


def test_add_data_source_to_bundle():
    expected_data_source = "ecr"
    bundle_result = add_data_source_to_bundle(valid_response, expected_data_source)
    for entry in bundle_result.get("entry", []):
        resource = entry.get("resource", {})
        assert expected_data_source in resource["meta"]["source"]


def test_add_data_source_to_bundle_missing_arg():
    expected_error_message = (
        "The data_source parameter must be a defined, non-empty string."
    )
    with pytest.raises(ValueError) as excinfo:
        add_data_source_to_bundle(valid_response, "")
    result_error_message = str(excinfo.value)
    assert expected_error_message in result_error_message


bundle_with_references = '<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><component><structuredBody><component><section><text><content styleCode="Bold">Additional Data</content><table><tbody><tr><th>Assigned Birth Sex</th><td ID="birthsex">Female</td></tr><tr><th>Gender Identity</th><td ID="gender-identity">unknown</td></tr><tr><th>Sexual Orientation</th><td ID="sexual-orientation">Do not know</td></tr></tbody></table><content styleCode="Bold">Travel History</content><table><thead><tr><th>Date of Travel</th><th>Location</th></tr></thead><tbody><tr><td>January 18th, 2018 - February 18th, 2018</td><td ID="trvhx-1">Traveled to Singapore, Malaysia and Bali with<br/>my family.</td></tr></tbody></table></text><entry><observation classCode="OBS" moodCode="EVN"><value code="F" codeSystem="2.16.840.1.113883.5.1" codeSystemName="AdministrativeGender" displayName="Female" xsi:type="CD"><originalText><reference value="#birthsex"/></originalText></value></observation></entry><entry><observation classCode="OBS" moodCode="EVN"><value nullFlavor="UNK" xsi:type="CD"><originalText><reference value="#gender-identity"/></originalText></value></observation></entry><entry><observation classCode="OBS" moodCode="EVN"><value nullFlavor="UNK" xsi:type="CD"><originalText><reference value="#sexual-orientation"/></originalText></value></observation></entry><entry><act classCode="ACT" moodCode="EVN"><text><reference value="#trvhx-1"/></text></act></entry></section></component></structuredBody></component></ClinicalDocument>'


def test_resolve_references_valid_input():
    tree = etree.fromstring(resolve_references(bundle_with_references))
    actual_refs = tree.xpath("//hl7:reference", namespaces={"hl7": "urn:hl7-org:v3"})
    assert actual_refs[0].attrib["value"] == "#birthsex"
    assert actual_refs[0].text == "Female"
    assert actual_refs[1].attrib["value"] == "#gender-identity"
    assert actual_refs[1].text == "unknown"
    assert actual_refs[2].attrib["value"] == "#sexual-orientation"
    assert actual_refs[2].text == "Do not know"
    assert actual_refs[3].attrib["value"] == "#trvhx-1"
    assert (
        actual_refs[3].text
        == "Traveled to Singapore, Malaysia and Bali with my family."
    )


def test_resolve_references_invalid_input():
    actual = resolve_references("VXU or HL7 MESSAGE")
    assert actual == "VXU or HL7 MESSAGE"


assert 1 == 1
