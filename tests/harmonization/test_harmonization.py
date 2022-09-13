import pathlib

from phdi.harmonization import (
    standardize_hl7_datetimes,
    convert_hl7_batch_messages_to_list,
    standardize_country_code,
    standardize_phone,
    standardize_name,
)


def test_standardize_hl7_datetimes():
    message_1 = open(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "FileSingleMessageLongDate.hl7"
    ).read()
    message_2 = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageLongTZ.hl7"
    ).read()
    message_3 = open(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "FileSingleMessageInvalidSegments.hl7"
    ).read()

    assert (
        standardize_hl7_datetimes(message_1)
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514010000||VXU^V04"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|20180808000000|M|||||||||||||||||||||\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
        + "NK1|1||BRO^BROTHER^HL70063^^^^^|^^NEW GLARUS^WI^^^^^^^|\n"
        + "PV1||R||||||||||||||||||\n"
        + "RXA|0|999|20180809|20180809|08^HepB pediatric^CVX^90744^HepB pediatric^CPT"
        + "|1.0|||01^^^^^~38193939^WIR immunization id^IMM_ID^^^|\n"
    )
    assert (
        standardize_hl7_datetimes(message_2)
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514010000-0400||VXU^V04"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|20180808|M|||||||||||||||||||||\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
        + "NK1|1||BRO^BROTHER^HL70063^^^^^|^^NEW GLARUS^WI^^^^^^^|\n"
        + "PV1||R||||||||||||||||||\n"
        + "RXA|0|999|20180809|20180809|08^HepB pediatric^CVX^90744^HepB pediatric^CPT"
        + "|1.0|||01^^^^^~38193939^WIR immunization id^IMM_ID^^^|||||||||||NA\n"
    )
    # Test for invalid segments
    assert (
        standardize_hl7_datetimes(message_3)
        == "AAA|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31|"
        + "2020051411020600|P^|2.4^^|||ER\n"
        + "BBB|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "CCC|||||||||||02^^^^^|Y||||A\n"
    )


def test_convert_hl7_batch_messages_to_list():
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

    list1 = convert_hl7_batch_messages_to_list(TEST_STRING1)
    list2 = convert_hl7_batch_messages_to_list(TEST_STRING2)
    list3 = convert_hl7_batch_messages_to_list(TEST_STRING3)

    assert len(list1) == 2
    assert len(list2) == 0
    assert len(list3) == 1

    assert list1[0].startswith("MSH|")
    assert list1[1].startswith("MSH|")
    assert list3[0].startswith("MSH|")


def test_standardize_country_code():
    assert standardize_country_code("US") == "US"
    assert standardize_country_code("USA") == "US"
    assert standardize_country_code("United States of America") == "US"
    assert standardize_country_code("United states ") == "US"
    assert standardize_country_code("US", "alpha_3") == "USA"
    assert standardize_country_code("USA", "numeric") == "840"

    # Edge case testing: nonsense code and empty string
    assert standardize_country_code("zzz") is None
    assert standardize_country_code("") is None


def test_standardize_phone():
    # Working examples of "real" numbers
    assert standardize_phone("555-654-9876") == "+15556549876"
    assert standardize_phone("555 654 9876") == "+15556549876"
    # Now supply country information
    assert standardize_phone("123.234.6789", ["US"]) == "+11232346789"
    assert standardize_phone("798.612.3456", ["GB"]) == "+447986123456"
    # Now do it as a list
    assert standardize_phone(["555-654-1234", "919876543210"], countries=["IN"]) == [
        "+915556541234",
        "+919876543210",
    ]
    # Make sure we catch edge cases and bad inputs
    assert standardize_phone("") == ""
    assert standardize_phone(" ") == ""
    assert standardize_phone("gibberish") == ""
    assert standardize_phone("1234567890987654321") == ""
    assert standardize_phone("123") == ""


def test_standardize_name():
    # Basic case of input string
    raw_text = " 12 PhDi is ReaLLy KEWL !@#$ 34"
    assert (
        standardize_name(raw_text, trim=True, case="lower", remove_numbers=False)
        == "12 phdi is really kewl  34"
    )
    assert (
        standardize_name(raw_text, trim=True, remove_numbers=True, case="title")
        == "Phdi Is Really Kewl"
    )
    # Now check that it handles list inputs
    names = ["Johnny T. Walker", " Paul bunYAN", "J;R;R;tOlK.iE87n 999"]
    assert standardize_name(names, trim=True, remove_numbers=False) == [
        "JOHNNY T WALKER",
        "PAUL BUNYAN",
        "JRRTOLKIE87N 999",
    ]
