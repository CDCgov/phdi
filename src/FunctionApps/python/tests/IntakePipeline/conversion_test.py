from unittest import mock
import pytest

from IntakePipeline.conversion import (
    clean_message,
    convert_batch_messages_to_list,
    convert_message_to_fhir,
    get_file_type_mappings,
)


def test_clean_message():
    TEST_STRING1 = "\r\nHello\nWorld\r\n"
    TEST_STRING2 = "\nHello\r\nW\r\norld"
    TEST_STRING3 = "Hello World"
    TEST_STRING4 = "\u000bHello World\u001c"
    TEST_STRING5 = "\u000bHello\r\nWorld\u001c"

    assert clean_message(TEST_STRING1) == "Hello\nWorld"
    assert clean_message(TEST_STRING2) == "Hello\nW\norld"
    assert clean_message(TEST_STRING3) == "Hello World"
    assert clean_message(TEST_STRING4) == "Hello World"
    assert clean_message(TEST_STRING5) == "Hello\nWorld"


def test_convert_batch_messages_to_list():
    TEST_STRING1 = """
    MSH|blah|foo|test
    PID|some^text|blah
    OBX|foo||||bar^baz&foobar
    MSH|blah|foo|test
    PID|some^text|blah
    OBX|foo||||bar^baz&foobar
    """.replace(
        " ", ""
    )

    TEST_STRING2 = """
    FHS|^~&|WIR11.3.2|WIR|||20200514||1219144.update|||
    BHS|^~&|WIR11.3.2|WIR|||20200514|||||
    BTS|0|
    FTS|1|
    """.replace(
        " ", ""
    )

    TEST_STRING3 = """
    FHS|^~&|WIR11.3.2|WIR|||20200514||1219144.update|||
    BHS|^~&|WIR11.3.2|WIR|||20200514|||||
    MSH|^~&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514||VXU^V04|2020051411020600|P^|2.4^^|||ER
    PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^|20180808|M|||||||||||||||||||||
    PD1|||||||||||02^^^^^|Y||||A
    NK1|1||BRO^BROTHER^HL70063^^^^^|^^NEW GLARUS^WI^^^^^^^|
    BTS|5|
    FTS|1|
    """.replace(
        " ", ""
    )

    list1 = convert_batch_messages_to_list(TEST_STRING1)
    list2 = convert_batch_messages_to_list(TEST_STRING2)
    list3 = convert_batch_messages_to_list(TEST_STRING3)

    assert len(list1) == 2
    assert len(list2) == 0
    assert len(list3) == 1

    assert list1[0].startswith("MSH|")
    assert list1[1].startswith("MSH|")
    assert list3[0].startswith("MSH|")


@mock.patch("requests.post")
def test_convert_message_to_fhir_success(mock_fhir_post):
    mock_fhir_post.return_value = mock.Mock(
        status_code=200, json=lambda: {"hello": "world"}
    )

    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar"
    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        "some-token",
        "some-fhir-url",
    )

    mock_fhir_post.assert_called_with(
        url="some-fhir-url/$convert-data",
        json={
            "resourceType": "Parameters",
            "parameter": [
                {"name": "inputData", "valueString": message},
                {"name": "inputDataType", "valueString": "Hl7v2"},
                {
                    "name": "templateCollectionReference",
                    "valueString": "microsofthealth/fhirconverter:default",
                },
                {"name": "rootTemplate", "valueString": "VXU_V04"},
            ],
        },
        headers={"Authorization": "Bearer some-token"},
    )

    assert response == {"hello": "world"}


@mock.patch("requests.post")
def test_convert_message_to_fhir_failure(mock_fhir_post):
    mock_fhir_post.return_value = mock.Mock(
        status_code=400, json=lambda: {"hello": "world"}
    )

    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar"
    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        "some-token",
        "some-fhir-url",
    )

    mock_fhir_post.assert_called_with(
        url="some-fhir-url/$convert-data",
        json={
            "resourceType": "Parameters",
            "parameter": [
                {"name": "inputData", "valueString": message},
                {"name": "inputDataType", "valueString": "Hl7v2"},
                {
                    "name": "templateCollectionReference",
                    "valueString": "microsofthealth/fhirconverter:default",
                },
                {"name": "rootTemplate", "valueString": "VXU_V04"},
            ],
        },
        headers={"Authorization": "Bearer some-token"},
    )

    assert response == {}


@mock.patch("requests.post")
@mock.patch("logging.error")
def test_log_fhir_operationoutcome(mock_log, mock_fhir_post):
    mock_fhir_post.return_value = mock.Mock(
        status_code=400,
        json=lambda: {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "fatal",
                    "code": "code-invalid",
                    "diagnostic": "error-description",
                }
            ],
        },
    )

    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar"

    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        "some-token",
        "some-fhir-url",
    )

    mock_fhir_post.assert_called_with(
        url="some-fhir-url/$convert-data",
        json={
            "resourceType": "Parameters",
            "parameter": [
                {"name": "inputData", "valueString": message},
                {"name": "inputDataType", "valueString": "Hl7v2"},
                {
                    "name": "templateCollectionReference",
                    "valueString": "microsofthealth/fhirconverter:default",
                },
                {"name": "rootTemplate", "valueString": "VXU_V04"},
            ],
        },
        headers={"Authorization": "Bearer some-token"},
    )

    mock_log.assert_called_with(
        "Error during $convert-data -- Error processing: some-filename-0  "
        + "HTTP Code: 400  FHIR Severity: fatal  Code: code-invalid  Diagnostics: None"
    )

    assert response == {}


@mock.patch("requests.post")
@mock.patch("logging.error")
def test_log_generic_error(mock_log, mock_fhir_post):
    mock_fhir_post.return_value = mock.Mock(status_code=400, content=b"some-error")

    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar"

    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        "some-token",
        "some-fhir-url",
    )

    mock_fhir_post.assert_called_with(
        url="some-fhir-url/$convert-data",
        json={
            "resourceType": "Parameters",
            "parameter": [
                {"name": "inputData", "valueString": message},
                {"name": "inputDataType", "valueString": "Hl7v2"},
                {
                    "name": "templateCollectionReference",
                    "valueString": "microsofthealth/fhirconverter:default",
                },
                {"name": "rootTemplate", "valueString": "VXU_V04"},
            ],
        },
        headers={"Authorization": "Bearer some-token"},
    )

    mock_log.assert_called_with(
        "Error during $convert-data -- HTTP Code: 400, Response Content some-error"
    )

    assert response == {}


def test_get_filetype_mappings_valid_files():
    TEST_STRING1 = "decrypted/ELR/some-file.hl7"
    TEST_STRING2 = "decrypted/VXU/some-file.hl7"
    TEST_STRING3 = "decrypted/eICR/some-file.xml"

    out1 = get_file_type_mappings(TEST_STRING1)
    out2 = get_file_type_mappings(TEST_STRING2)
    out3 = get_file_type_mappings(TEST_STRING3)

    # spot check the outputs to make sure they're all fine
    assert out1["input_data_type"] == "Hl7v2"
    assert out3["input_data_type"] == "Ccda"
    assert out2["bundle_type"] == "VXU"
    assert out3["bundle_type"] == "ECR"
    assert out1["root_template"] == "ORU_R01"
    assert out2["root_template"] == "VXU_V04"
    assert out3["template_collection"] == "microsofthealth/ccdatemplates:default"


def test_get_filetype_mappings_invalid_extension():
    with pytest.raises(Exception):
        get_file_type_mappings("decrypted/ELR/some-file.txt")


def test_get_filetype_mappings_invalid_directory():
    with pytest.raises(Exception):
        get_file_type_mappings("decrypted/VISS/some-file.hl7")
