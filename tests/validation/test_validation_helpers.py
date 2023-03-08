import pathlib
from phdi.validation.validation import (
    _organize_error_messages,
    _match_nodes,
    _validate_attribute,
    _validate_text,
    _check_field_matches,
    _check_custom_message,
    # namespaces,
)
from lxml import etree


# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml"
).read()


def test_organize_error_messages():
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    test_include_errors = ["fatal", "error", "warning", "information"]

    expected_result = {
        "fatal": fatal,
        "errors": errors,
        "warnings": warns,
        "information": infos,
    }

    actual_result = _organize_error_messages(
        fatal=fatal,
        errors=errors,
        warnings=warns,
        information=infos,
        include_error_types=test_include_errors,
    )
    assert actual_result == expected_result

    fatal = []
    test_include_errors = ["information"]

    expected_result = {"fatal": [], "errors": [], "warnings": [], "information": infos}

    actual_result = _organize_error_messages(
        fatal, errors, warns, infos, test_include_errors
    )
    assert actual_result == expected_result

    test_include_errors = ["fatal"]
    expected_result = {"fatal": fatal, "errors": [], "warnings": [], "information": []}
    actual_result = _organize_error_messages(
        fatal, errors, warns, infos, test_include_errors
    )
    assert actual_result == expected_result


def test_match_nodes():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test'><bar/><baz><biz/></baz><biz/></foo>"
    root = etree.fromstring(xml)

    config = {"parent": "foo", "fieldName": "bar", "cdaPath": "//test:foo/test:bar"}
    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)

    config_biz = {
        "parent": "baz",
        "fieldName": "biz",
        "cdaPath": "//test:foo/test:baz/test:biz",
    }
    xml_elements_biz = root.xpath(config_biz.get("cdaPath"), namespaces=namespace)

    assert _match_nodes([], config) == []
    assert _match_nodes(xml_elements, config) == [xml_elements[0]]
    assert _match_nodes(xml_elements_biz, config_biz) == [xml_elements_biz[0]]
    assert len(_match_nodes(xml_elements_biz, config_biz)) == 1


def test_check_field_matches():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test'><bar/><baz><biz/></baz><biz/><taz/></foo>"
    root = etree.fromstring(xml)

    config = {"parent": "foo", "fieldName": "bar", "cdaPath": "//test:foo/test:bar"}
    config_false_cda_path = {
        "parent": "foo",
        "fieldName": "biz",
        "cdaPath": "//test:foo/test:biz",
    }
    config_false_attributes = {
        "parent": "foo",
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
        "attributes": [{"attributeName": "test"}],
    }

    config_check_all = {
        "parent": "foo",
        "fieldName": "taz",
        "cdaPath": "//test:foo/test:taz",
        "attributes": [{"attributeName": "test"}],
        "validateAll": "True",
    }
    config_dont_check_all = {
        "parent": "foo",
        "fieldName": "taz",
        "cdaPath": "//test:foo/test:taz",
        "attributes": [{"attributeName": "test"}],
        "validateAll": "False",
    }
    config_dont_check_all_default = {
        "parent": "foo",
        "fieldName": "taz",
        "cdaPath": "//test:foo/test:taz",
        "attributes": [{"attributeName": "test"}],
    }
    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    xml_elements_bar = root.xpath(
        config_false_attributes.get("cdaPath"), namespaces=namespace
    )
    xml_elements_taz = root.xpath(config_check_all.get("cdaPath"), namespaces=namespace)

    assert _check_field_matches(xml_elements[0], config)
    assert not _check_field_matches(xml_elements[0], config_false_cda_path)
    assert not _check_field_matches(xml_elements_bar[0], config_false_attributes)
    assert _check_field_matches(xml_elements_taz[0], config_check_all)
    assert not _check_field_matches(xml_elements_taz[0], config_dont_check_all)
    assert not _check_field_matches(xml_elements_taz[0], config_dont_check_all_default)


def test_validate_attribute():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test'><bar test='bat'/><baz><biz/></baz><biz/></foo>"
    root = etree.fromstring(xml)

    config = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
    }
    config_attributes = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "fail"}],
        "cdaPath": "//test:foo/test:bar",
    }
    config_reg_ex = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test", "regEx": "bar"}],
        "cdaPath": "//test:foo/test:bar",
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    assert _validate_attribute(xml_elements[0], config) == []
    assert _validate_attribute(xml_elements[0], config_attributes) == [
        "Could not find attribute fail for tag bar"
    ]
    assert _validate_attribute(xml_elements[0], config_reg_ex) == [
        "Attribute: 'test' for field: 'bar' not in expected format"
    ]


def test_validate_text():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test'><bar>test</bar><baz><biz/></baz><biz>wrong</biz></foo>"
    root = etree.fromstring(xml)

    config = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    assert _validate_text(xml_elements[0], config) == []

    config_no_text = {
        "fieldName": "biz",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:baz/test:biz",
        "textRequired": "True",
    }

    xml_elements = root.xpath(config_no_text.get("cdaPath"), namespaces=namespace)
    assert _validate_text(xml_elements[0], config_no_text) == [
        "Field: biz does not have text"
    ]

    config_text_matches_reg_ex = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "test",
    }
    xml_elements = root.xpath(
        config_text_matches_reg_ex.get("cdaPath"), namespaces=namespace
    )
    assert _validate_text(xml_elements[0], config_text_matches_reg_ex) == []

    config_text_doesnt_match_reg_ex = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "foo",
    }
    xml_elements = root.xpath(
        config_text_doesnt_match_reg_ex.get("cdaPath"), namespaces=namespace
    )
    assert _validate_text(xml_elements[0], config_text_doesnt_match_reg_ex) == [
        "Field: bar does not match regEx: foo"
    ]


def test_check_custom_message():
    config_field_with_custom = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "foo",
        "customMessage": "this is a custom message",
    }
    result = _check_custom_message(
        config_field_with_custom, "this is a default message"
    )
    assert result == "this is a custom message"

    config_field_no_custom = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "foo",
    }
    result = _check_custom_message(config_field_no_custom, "this is a default message")
    assert result == "this is a default message"
