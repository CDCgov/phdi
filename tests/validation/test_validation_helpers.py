import pathlib
from phdi.validation.validation import (
    _organize_error_messages,
    _match_nodes,
    _validate_attribute,
    _validate_text,
    _check_field_matches,
    _response_builder,
    _check_custom_message,
    _get_xml_message_id,
    _get_attributes_list,
    _get_field_details_string,
    _find_related_element,
    _check_relatives,
    RR_MSG_ID_XPATH,
    EICR_MSG_ID_XPATH,
    namespaces,
)
from lxml import etree


test_include_errors = ["fatal", "errors", "warnings", "information"]

# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

# Test good file with RR data
sample_file_good_RR = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "ecr_sample_input_good_with_RR.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml"
).read()


def test_organize_error_messages():
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    test_include_errors = ["fatal", "errors", "warnings", "information"]
    msg_ids = {}

    expected_result = {
        "fatal": fatal,
        "errors": errors,
        "warnings": warns,
        "information": infos,
        "message_ids": msg_ids,
    }

    actual_result = _organize_error_messages(
        fatal=fatal,
        errors=errors,
        warnings=warns,
        information=infos,
        message_ids=msg_ids,
        include_error_types=test_include_errors,
    )
    assert actual_result == expected_result

    fatal = []
    test_include_errors = ["information"]

    expected_result = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": infos,
        "message_ids": msg_ids,
    }

    actual_result = _organize_error_messages(
        fatal=fatal,
        errors=errors,
        warnings=warns,
        information=infos,
        message_ids=msg_ids,
        include_error_types=test_include_errors,
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
        "Could not find attribute fail. Field name: 'bar' Attributes: name: 'fail'"
    ]
    assert _validate_attribute(xml_elements[0], config_reg_ex) == [
        "Attribute: 'test' not in expected format. Field name: 'bar' Attributes: name:"
        + " 'test' RegEx: 'bar' value: 'bat'"
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
        "Field does not have text. Field name: 'biz' value: '' Attributes: name: 'test'"
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
        "Field does not match regEx: foo. Field name: 'bar' value: 'test' Attributes:"
        + " name: 'test'"
    ]


def test_response_builder():
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {},
        },
        "validated_message": sample_file_good,
    }
    result = _response_builder(
        errors=expected_response["validation_results"],
        msg=sample_file_good,
        include_error_types=test_include_errors,
    )

    assert result == expected_response


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


def test_get_xml_message_id():
    # parse and prep data from example file
    # for testing
    xml = sample_file_good_RR.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    parsed_ecr = etree.fromstring(xml, parser=parser)

    actual_result = _get_xml_message_id(
        parsed_ecr.xpath(EICR_MSG_ID_XPATH, namespaces=namespaces)
    )
    expected_result = {
        "root": "2.16.840.1.113883.9.9.9.9.9",
        "extension": "db734647-fc99-424c-a864-7e3cda82e704",
    }
    assert actual_result == expected_result

    expected_result = {
        "root": "4efa0e5c-c34c-429f-b5de-f1a13aef4a28",
        "extension": None,
    }
    actual_result = _get_xml_message_id(
        parsed_ecr.xpath(RR_MSG_ID_XPATH, namespaces=namespaces)
    )
    assert actual_result == expected_result


def test_get_field_details_string():
    namespace = {"test": "test"}
    xml = (
        "<foo xmlns='test'><bar test='hello'>test</bar><baz><biz/></baz>"
        + "<biz>wrong</biz></foo>"
    )
    root = etree.fromstring(xml)
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
    assert (
        _get_field_details_string(xml_elements[0], config_text_matches_reg_ex)
        == "Field name: 'bar' value: 'test' Attributes: name: 'test' value: 'hello'"
    )


def test_get_attributes_list():
    namespace = {"test": "test"}
    xml = (
        "<foo xmlns='test'><bar test='hello'>test</bar><baz><biz/></baz>"
        + "<biz>wrong</biz></foo>"
    )
    root = etree.fromstring(xml)
    config_text_matches_reg_ex = {
        "fieldName": "bar",
        "attributes": [
            {"attributeName": "test", "regEx": "test"},
            {"attributeName": "foo"},
        ],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "test",
    }

    xml_elements = root.xpath(
        config_text_matches_reg_ex.get("cdaPath"), namespaces=namespace
    )
    assert _get_attributes_list(
        config_text_matches_reg_ex.get("attributes"), xml_elements[0]
    ) == ["name: 'test' RegEx: 'test' value: 'hello', name: 'foo'"]


def test_find_related_element():
    namespace = {"test": "test"}
    xml = (
        "<foo xmlns='test'><chaz/><bar test='hello'><baz foo='bar'><biz/></baz></bar>"
        + "<biz>wrong</biz></foo>"
    )
    root = etree.fromstring(xml)
    config = {
        "fieldName": "bar",
        "attributes": [
            {"attributeName": "test", "regEx": "test"},
            {"attributeName": "foo"},
        ],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "test",
        "relatives": [
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
                "attributes": [{"attributeName": "foo", "regEx": "bar"}],
            },
            {"name": "foo", "cdaPath": "//test:foo"},
            {"name": "biz", "cdaPath": "//test:foo/test:biz"},
            {"name": "chaz", "cdaPath": "//test:foo/test:chaz"},
            {
                "name": "Not found",
                "cdaPath": "//test:foo/test:bar/test:notFound",
                "attributes": [{"attributeName": "foo", "regEx": "bar"}],
            },
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
                "attributes": [{"attributeName": "foo", "regEx": "bat"}],
            },
        ],
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)

    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[0],
        ).tag
        == "{test}baz"
    )
    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[1],
        ).tag
        == "{test}foo"
    )

    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[2],
        ).tag
        == "{test}biz"
    )

    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[3],
        ).tag
        == "{test}chaz"
    )

    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[4],
        )
        is False
    )

    assert (
        _find_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[5],
        )
        is False
    )

    assert (
        _find_related_element(
            None,
            config.get("cdaPath"),
            config.get("relatives")[0],
        )
        is False
    )


def test_check_relatives():
    namespace = {"test": "test"}
    xml = (
        "<foo xmlns='test'><chaz/><bar test='hello'><baz foo='bar'><biz/></baz></bar>"
        + "<biz>wrong</biz></foo>"
    )
    root = etree.fromstring(xml)
    config = {
        "fieldName": "bar",
        "attributes": [
            {"attributeName": "test", "regEx": "test"},
            {"attributeName": "foo"},
        ],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "test",
        "relatives": [
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
                "attributes": [{"attributeName": "foo", "regEx": "bar"}],
            },
            {"name": "foo", "cdaPath": "//test:foo"},
            {"name": "biz", "cdaPath": "//test:foo/test:biz"},
            {"name": "chaz", "cdaPath": "//test:foo/test:chaz"},
            {
                "name": "Not found",
                "cdaPath": "//test:foo/test:bar/test:notFound",
                "attributes": [{"attributeName": "foo", "regEx": "bar"}],
            },
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
                "attributes": [{"attributeName": "foo", "regEx": "bat"}],
            },
        ],
    }

    config_correct = {
        "fieldName": "bar",
        "attributes": [
            {"attributeName": "test", "regEx": "test"},
            {"attributeName": "foo"},
        ],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "test",
        "relatives": [
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
                "attributes": [{"attributeName": "foo", "regEx": "bar"}],
            },
            {"name": "foo", "cdaPath": "//test:foo"},
            {"name": "biz", "cdaPath": "//test:foo/test:biz"},
            {"name": "chaz", "cdaPath": "//test:foo/test:chaz"},
        ],
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    assert _check_relatives(xml_elements[0], config) is False
    assert _check_relatives(xml_elements[0], config_correct) is True
