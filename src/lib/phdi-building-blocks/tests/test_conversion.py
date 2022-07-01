import hl7
import pathlib
import pytest

from unittest import mock
from phdi_building_blocks.conversion import (
    clean_batch,
    clean_message,
    convert_batch_messages_to_list,
    convert_message_to_fhir,
    get_file_type_mappings,
    normalize_hl7_datetime,
    normalize_hl7_datetime_segment,
)


def test_clean_batch():
    TEST_STRING1 = "\r\nHello\nWorld\r\n"
    TEST_STRING2 = "\nHello\r\nW\r\norld"
    TEST_STRING3 = "Hello World"
    TEST_STRING4 = "\u000bHello World\u001c"
    TEST_STRING5 = "\u000bHello\r\nWorld\u001c"

    assert clean_batch(TEST_STRING1) == "Hello\nWorld"
    assert clean_batch(TEST_STRING2) == "Hello\nW\norld"
    assert clean_batch(TEST_STRING3) == "Hello World"
    assert clean_batch(TEST_STRING4) == "Hello World"
    assert clean_batch(TEST_STRING5) == "Hello\nWorld"


def test_clean_message():
    message_1 = open(
        pathlib.Path(__file__).parent / "assets" / "FileSingleMessageLongDate.hl7"
    ).read()
    message_2 = open(
        pathlib.Path(__file__).parent / "assets" / "FileSingleMessageLongTZ.hl7"
    ).read()

    assert clean_message(message_1).startswith(
        "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514010000|"
        + "|VXU^V04|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|"
        + "HEPB^DTAP^^^^^^|20180808000000|M|||||||||||||||||||||"
    )
    assert clean_message(message_2).startswith(
        "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514010000-0400|"
        + "|VXU^V04|2020051411020600|P^|2.4^^|||ER"
    )


def test_normalize_hl7_datetime_segment():
    message_1 = (
        open(pathlib.Path(__file__).parent / "assets" / "FileSingleMessageLongDate.hl7")
        .read()
        .replace("\n", "\r")
    )

    message_1_parsed = hl7.parse(message_1)

    normalize_hl7_datetime_segment(message_1_parsed, "PID", [7])

    assert str(message_1_parsed).startswith(
        "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|202005140100001234567890|"
        + "|VXU^V04|2020051411020600|P^|2.4^^|||ER\r"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|"
        + "HEPB^DTAP^^^^^^|20180808000000|M|||||||||||||||||||||"
    )


def test_normalize_hl7_datetime():
    datetime_0 = ""
    datetime_1 = "20200514010000"
    datetime_2 = "202005140100005555"
    datetime_3 = "20200514"
    datetime_4 = "20200514.123456"
    datetime_5 = "20200514+0400000"
    datetime_6 = "20200514.123456-070000"
    datetime_7 = "20200514010000.1234-0700"
    datetime_8 = "not-a-date"

    assert normalize_hl7_datetime(datetime_0) == ""
    assert normalize_hl7_datetime(datetime_1) == "20200514010000"
    assert normalize_hl7_datetime(datetime_2) == "20200514010000"
    assert normalize_hl7_datetime(datetime_3) == "20200514"
    assert normalize_hl7_datetime(datetime_4) == "20200514.1234"
    assert normalize_hl7_datetime(datetime_5) == "20200514+0400"
    assert normalize_hl7_datetime(datetime_6) == "20200514.1234-0700"
    assert normalize_hl7_datetime(datetime_7) == "20200514010000.1234-0700"
    assert normalize_hl7_datetime(datetime_8) == "not-a-date"


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


@mock.patch("requests.Session")
def test_convert_message_to_fhir_success(mock_requests_session):

    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {"resourceType": "Bundle", "entry": [{"hello": "world"}]},
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"
    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    assert response.status_code == 200
    assert response.json() == {"resourceType": "Bundle", "entry": [{"hello": "world"}]}


@mock.patch("requests.Session")
def test_convert_message_to_fhir_failure(mock_requests_session):

    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400,
        text='{ "resourceType": "Bundle", "entry": [{"hello": "world"}] }',
    )

    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"
    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    assert response.status_code == 400
    assert (
        response.text
        == '{ "resourceType": "Bundle", "entry": ' + '[{"hello": "world"}] }'
    )


@mock.patch("requests.Session")
@mock.patch("logging.error")
def test_log_fhir_operationoutcome(mock_log, mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400,
        text='{ "resourceType": "OperationOutcome", "diagnostics": "some-error" }',
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"

    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    assert response.status_code == 400
    assert (
        response.text
        == '{ "resourceType": "OperationOutcome", ' + '"diagnostics": "some-error" }'
    )


@mock.patch("requests.Session")
@mock.patch("logging.error")
def test_log_generic_error(mock_log, mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value
    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400, text="some-error"
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"
    convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    mock_log.assert_called_with(
        "HTTP 400 code encountered on $convert-data for some-filename-0"
    )


@mock.patch("requests.Session")
@mock.patch("logging.error")
def test_generic_error(mock_log, mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400, text="some-error"
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"

    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    assert response.status_code == 400
    assert response.text == "some-error"


@mock.patch("requests.Session")
@mock.patch("logging.error")
def test_error_with_special_chars(mock_log, mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400, text="some-error with \" special ' characters \n"
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    message = "MSH|blah|foo|test\nPID|some^text|blah\nOBX|foo||||bar^baz&foobar\n"

    response = convert_message_to_fhir(
        message,
        "some-filename-0",
        "Hl7v2",
        "VXU_V04",
        "microsofthealth/fhirconverter:default",
        mock_cred_manager,
        "some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-fhir-url/$convert-data",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
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
    )

    assert response.status_code == 400
    assert response.text == "some-error with \" special ' characters \n"


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
