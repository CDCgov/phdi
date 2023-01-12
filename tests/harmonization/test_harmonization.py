import fuzzy
import hl7
import pathlib

from phdi.harmonization import (
    convert_hl7_batch_messages_to_list,
    default_hl7_value,
    double_metaphone_string,
    normalize_hl7_datetime,
    normalize_hl7_datetime_segment,
    standardize_country_code,
    standardize_hl7_datetimes,
    standardize_name,
    standardize_phone,
)


def test_double_metaphone_string():

    # Two test conditions: one in which dmeta is created within each
    # function call, and another where it's initiated outside the call
    # and passed in repeatedly to simulate bulk processing
    for dmeta in [None, fuzzy.DMetaphone()]:

        # Test 1: phonetically similar names (i.e. names that sound
        # the same) should map to the same encoding
        assert double_metaphone_string("John", dmeta) == double_metaphone_string(
            "Jon", dmeta
        )
        assert double_metaphone_string("John", dmeta) == double_metaphone_string(
            "Jhon", dmeta
        )
        assert double_metaphone_string("Michelle", dmeta) == double_metaphone_string(
            "Michel", dmeta
        )
        assert double_metaphone_string("Deanardo", dmeta) == double_metaphone_string(
            "Dinardio", dmeta
        )
        assert double_metaphone_string(
            "Beaumarchais", dmeta
        ) == double_metaphone_string("Bumarchay", dmeta)
        assert double_metaphone_string("Sophia", dmeta) == double_metaphone_string(
            "Sofia", dmeta
        )

        # Test 2: names with language-dependent pronunciation (e.g. German
        # pronunciation of 'W' as 'V') should have secondary encodings
        # that reflect this
        michael = double_metaphone_string("Michael", dmeta)
        mikael = double_metaphone_string("Mikael", dmeta)
        assert michael[0] == mikael[0] and michael[1] != mikael[1]
        wagner = double_metaphone_string("Wagner", dmeta)
        assert wagner[1] is not None and wagner[0] != wagner[1]
        filipowitz = double_metaphone_string("Filipowitz", dmeta)
        assert filipowitz[1] is not None and filipowitz[0] != filipowitz[1]

        # Test 3: correctly spelled name should map to the same phonetics as a
        # misspelled or incomplete root/derivative stem of the name
        assert double_metaphone_string("Johnson", dmeta) == double_metaphone_string(
            "Jhnson", dmeta
        )
        assert double_metaphone_string("Williams", dmeta) == double_metaphone_string(
            "Wiliams", dmeta
        )
        assert double_metaphone_string("Harper", dmeta) == double_metaphone_string(
            "Harpr", dmeta
        )
        assert double_metaphone_string("Harper", dmeta) == double_metaphone_string(
            "Harpur", dmeta
        )

        # Test 4: Make sure both formats can handle an empty string
        assert double_metaphone_string("", dmeta) == [None, None]


def test_standardize_hl7_datetimes():
    message_long_date = open(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "FileSingleMessageLongDate.hl7"
    ).read()
    massage_timezone = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageLongTZ.hl7"
    ).read()
    massage_invalid_segments = open(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "FileSingleMessageInvalidSegments.hl7"
    ).read()

    assert (
        standardize_hl7_datetimes(message_long_date)
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
        standardize_hl7_datetimes(massage_timezone)
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
        standardize_hl7_datetimes(massage_invalid_segments)
        == "AAA|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31|"
        + "2020051411020600|P^|2.4^^|||ER\n"
        + "BBB|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "CCC|||||||||||02^^^^^|Y||||A\n"
    )


def test_normalize_hl7_datetime_segment():
    message_long_date = (
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "FileSingleMessageLongDate.hl7"
        )
        .read()
        .replace("\n", "\r")
    )

    message_long_date_parsed = hl7.parse(message_long_date)

    normalize_hl7_datetime_segment(message_long_date_parsed, "PID", [7])

    assert str(message_long_date_parsed).startswith(
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
    message_default_invalid_field = open(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "FileSingleMessageInvalidSegments.hl7"
    ).read()
    message_default_invalid_segment = open(
        pathlib.Path(__file__).parent.parent / "assets" / "FileSingleMessageSimple.hl7"
    ).read()

    message_default_empty_field = default_hl7_value(
        message=message_default_empty_field,
        segment_id="PID",
        field_num=1,
        default_value="some-default-value-empty",
    )
    message_default_missing_field = default_hl7_value(
        message=message_default_missing_field,
        segment_id="PID",
        field_num=30,
        default_value="some-default-value-missing",
    )
    message_default_populated_field = default_hl7_value(
        message=message_default_populated_field,
        segment_id="PID",
        field_num=5,
        default_value="some-default-value-populated",
    )
    message_default_invalid_segment = default_hl7_value(
        message=message_default_invalid_segment,
        segment_id="BAD",
        field_num=5,
        default_value="some-default-value-populated",
    )
    message_default_invalid_field = default_hl7_value(
        message=message_default_invalid_field,
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
    assert (
        message_default_invalid_field
        == "AAA|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31|"
        + "2020051411020600|P^|2.4^^|||ER\n"
        + "BBB|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "CCC|||||||||||02^^^^^|Y||||A\n"
    )
    assert (
        message_default_invalid_segment
        == "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|2020051401000000||ADT^A31"
        + "|2020051411020600|P^|2.4^^|||ER\n"
        + "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^"
        + "|2018080800000000000|M|||||||||||||||||||||\n"
        + "PD1|||||||||||02^^^^^|Y||||A\n"
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
