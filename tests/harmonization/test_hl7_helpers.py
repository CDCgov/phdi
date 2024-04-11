from phdi.harmonization.hl7 import _clean_hl7_batch


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
