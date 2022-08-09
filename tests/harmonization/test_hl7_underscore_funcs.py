import hl7
import pathlib

from phdi.harmonization.hl7 import (
    _default_hl7_value,
    _normalize_hl7_datetime_segment,
    _normalize_hl7_datetime,
    _clean_hl7_batch,
)


def test_default_hl7_value():
    message_default_empty_field = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageSimple.hl7"
    ).read()

    message_default_missing_field = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageSimple.hl7"
    ).read()

    message_default_populated_field = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageSimple.hl7"
    ).read()

    message_default_empty_field = _default_hl7_value(
        message=message_default_empty_field,
        segment_id="PID",
        field_num=1,
        default_value="some-default-value-empty",
    )
    message_default_missing_field = _default_hl7_value(
        message=message_default_missing_field,
        segment_id="PID",
        field_num=30,
        default_value="some-default-value-missing",
    )
    message_default_populated_field = _default_hl7_value(
        message=message_default_populated_field,
        segment_id="PID",
        field_num=5,
        default_value="some-default-value-populated",
    )

    assert (
        message_default_empty_field
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|some-default-value-empty||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^"
        + "|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
    )
    assert (
        message_default_missing_field
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M||||||||||||||||||||||some-default-value-missing\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
    )
    assert (
        message_default_populated_field
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
    )


def test_normalize_hl7_datetime_segment():
    message_1 = (
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "FileSingleMessageLongDate.hl7"
        )
        .read()
        .replace("\n", "\r")
    )

    message_1_parsed = hl7.parse(message_1)

    _normalize_hl7_datetime_segment(message_1_parsed, "PID", [7])

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

    assert _normalize_hl7_datetime(datetime_0) == ""
    assert _normalize_hl7_datetime(datetime_1) == "20200514010000"
    assert _normalize_hl7_datetime(datetime_2) == "20200514010000"
    assert _normalize_hl7_datetime(datetime_3) == "20200514"
    assert _normalize_hl7_datetime(datetime_4) == "20200514.1234"
    assert _normalize_hl7_datetime(datetime_5) == "20200514+0400"
    assert _normalize_hl7_datetime(datetime_6) == "20200514.1234-0700"
    assert _normalize_hl7_datetime(datetime_7) == "20200514010000.1234-0700"
    assert _normalize_hl7_datetime(datetime_8) == "not-a-date"


def test_clean_hl7_batch():
    TEST_STRING1 = "\r\nHello\nWorld\r\n"
    TEST_STRING2 = "\nHello\r\nW\r\norld"
    TEST_STRING3 = "Hello World"
    TEST_STRING4 = "\u000bHello World\u001c"
    TEST_STRING5 = "\u000bHello\r\nWorld\u001c"

    assert _clean_hl7_batch(TEST_STRING1) == "Hello\nWorld"
    assert _clean_hl7_batch(TEST_STRING2) == "Hello\nW\norld"
    assert _clean_hl7_batch(TEST_STRING3) == "Hello World"
    assert _clean_hl7_batch(TEST_STRING4) == "Hello World"
    assert _clean_hl7_batch(TEST_STRING5) == "Hello\nWorld"
