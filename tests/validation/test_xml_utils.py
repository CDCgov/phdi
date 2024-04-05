import pathlib

from lxml import etree

from phdi.validation.xml_utils import _check_xml_names_and_attribs_exist
from phdi.validation.xml_utils import _get_ecr_custom_message
from phdi.validation.xml_utils import _get_xml_attributes
from phdi.validation.xml_utils import _get_xml_message_id
from phdi.validation.xml_utils import _get_xml_relative_iterator
from phdi.validation.xml_utils import _get_xml_relatives_details
from phdi.validation.xml_utils import _validate_xml_related_element
from phdi.validation.xml_utils import _validate_xml_relatives
from phdi.validation.xml_utils import ECR_NAMESPACES
from phdi.validation.xml_utils import EICR_MSG_ID_XPATH
from phdi.validation.xml_utils import get_ecr_message_ids
from phdi.validation.xml_utils import get_xml_element_details
from phdi.validation.xml_utils import RR_MSG_ID_XPATH
from phdi.validation.xml_utils import validate_xml_attributes
from phdi.validation.xml_utils import validate_xml_elements
from phdi.validation.xml_utils import validate_xml_value

test_include_errors = ["fatal", "errors", "warnings", "information"]

# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_good.xml"
).read()

# Test good file with RR data
sample_file_good_RR = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_good_with_RR.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "sample_ecr_config.yaml"
).read()


def test_validate_xml_elements():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test' use='L'><bar>Blah<baz><biz></biz></baz></bar></foo>"
    root = etree.fromstring(xml)

    proper_config = {
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
        "errorType": "fatal",
        "textRequired": "True",
        "validateOne": False,
        "relatives": [
            {
                "name": "foo",
                "cdaPath": "//test:foo",
                "attributes": [{"attributeName": "use", "regEx": "L"}],
            }
        ],
    }

    xml_elements = root.xpath("//test:foo/test:bar", namespaces=namespace)
    config_biz = {
        "fieldName": "biz",
        "cdaPath": "//test:foo/test:bar/test:baz/test:biz",
        "errorType": "fatal",
        "relatives": [{"name": "baz", "cdaPath": "//test:foo/test:bar/test:baz"}],
    }
    xml_elements_biz = root.xpath(config_biz.get("cdaPath"), namespaces=namespace)

    assert validate_xml_elements([], config) == []
    assert validate_xml_elements(xml_elements, proper_config) == [xml_elements[0]]
    assert validate_xml_elements(xml_elements_biz, config_biz) == [xml_elements_biz[0]]
    assert len(validate_xml_elements(xml_elements_biz, config_biz)) == 1

    # now let's make it fail and return none based upon the config
    wrong_config = {
        "fieldName": "biz",
        "cdaPath": "//test:foo/test:bar/test:baz/test:biz",
        "errorType": "fatal",
        "relatives": [{"name": "baz", "cdaPath": "//test:foo/test:bar/test:booty"}],
    }
    assert validate_xml_elements(xml_elements_biz, wrong_config) == []


def test_get_xml_relative_iterator():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test' use='L'><bar>Blah<baz><biz></biz></baz></bar></foo>"
    root = etree.fromstring(xml)

    proper_config = {
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
        "errorType": "fatal",
        "textRequired": "True",
        "validateOne": False,
        "relatives": [
            {
                "name": "foo",
                "cdaPath": "//test:foo",
                "attributes": [{"attributeName": "use", "regEx": "L"}],
            }
        ],
    }
    xml_elements = root.xpath("//test:foo/test:bar", namespaces=namespace)
    result = _get_xml_relative_iterator(
        cda_path=proper_config["cdaPath"],
        relative_cda_path=proper_config.get("relatives")[0].get("cdaPath"),
        xml_element=xml_elements[0],
    )
    assert result.tag == "{test}foo"

    child_config = {
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
        "errorType": "fatal",
        "textRequired": "True",
        "validateOne": False,
        "relatives": [
            {
                "name": "baz",
                "cdaPath": "//test:foo/test:bar/test:baz",
            }
        ],
    }

    result = _get_xml_relative_iterator(
        cda_path=child_config["cdaPath"],
        relative_cda_path=child_config.get("relatives")[0].get("cdaPath"),
        xml_element=xml_elements[0],
    )
    child_tag = ""
    for childs in result:
        child_tag = childs.tag
    assert child_tag == "{test}baz"

    anc_config = {
        "fieldName": "baz",
        "cdaPath": "//test:foo/test:bar/test:baz",
        "errorType": "fatal",
        "textRequired": "True",
        "validateOne": False,
        "relatives": [
            {
                "name": "foo",
                "cdaPath": "//test:foo",
            }
        ],
    }

    xml_elements = root.xpath("//test:foo/test:bar/test:baz", namespaces=namespace)

    result = _get_xml_relative_iterator(
        cda_path=anc_config["cdaPath"],
        relative_cda_path=anc_config.get("relatives")[0].get("cdaPath"),
        xml_element=xml_elements[0],
    )
    assert result.tag == "{test}foo"

    sib_config = {
        "fieldName": "baz",
        "cdaPath": "//test:foo/test:bar/test:baz",
        "errorType": "fatal",
        "textRequired": "True",
        "validateOne": False,
        "relatives": [
            {
                "name": "beep",
                "cdaPath": "//test:foo/test:bar/test:beep",
            }
        ],
    }

    namespace = {"test": "test"}
    xml3 = (
        "<foo xmlns='test' use='L'><bar>Blah<baz><biz>"
        + "</biz></baz><beep></beep></bar></foo>"
    )
    root3 = etree.fromstring(xml3)
    xml_elements3 = root3.xpath("//test:foo/test:bar/test:baz", namespaces=namespace)
    result = _get_xml_relative_iterator(
        cda_path=sib_config["cdaPath"],
        relative_cda_path=sib_config.get("relatives")[0].get("cdaPath"),
        xml_element=xml_elements3[0],
    )
    sib_tag = ""
    for sibs in result:
        sib_tag = sibs.tag
    assert sib_tag == "{test}beep"

    result = _get_xml_relative_iterator(
        cda_path=proper_config["cdaPath"],
        relative_cda_path=proper_config.get("relatives")[0].get("cdaPath"),
        xml_element=None,
    )

    assert result is None


def test_check_xml_names_and_attribs_exist():
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

    assert _check_xml_names_and_attribs_exist(xml_elements[0], config)
    assert not _check_xml_names_and_attribs_exist(
        xml_elements[0], config_false_cda_path
    )
    assert not _check_xml_names_and_attribs_exist(
        xml_elements_bar[0], config_false_attributes
    )
    assert _check_xml_names_and_attribs_exist(xml_elements_taz[0], config_check_all)
    assert not _check_xml_names_and_attribs_exist(
        xml_elements_taz[0], config_dont_check_all
    )
    assert not _check_xml_names_and_attribs_exist(
        xml_elements_taz[0], config_dont_check_all_default
    )


def test_validate_xml_attributes():
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

    config_no_attr = {
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    result = validate_xml_attributes(xml_elements[0], config)
    assert result == []
    result = validate_xml_attributes(xml_elements[0], config_attributes)
    assert result == [
        "Could not find attribute 'fail'. Field name: 'bar' Attributes: "
        + "attribute #1: 'fail'"
    ]
    result = validate_xml_attributes(xml_elements[0], config_reg_ex)
    assert result == [
        "Attribute: 'test' not in expected format. Field name:"
        + " 'bar' Attributes: attribute #1: 'test' with the "
        + "required value pattern: 'bar' actual value: 'bat'"
    ]

    result = validate_xml_attributes(xml_elements[0], config_no_attr)
    assert result == []


def test_validate_xml_value():
    namespace = {"test": "test"}
    xml = "<foo xmlns='test'><bar>test</bar><baz><biz/></baz><biz>wrong</biz></foo>"
    root = etree.fromstring(xml)

    okconfig = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
    }

    xml_elements = root.xpath(okconfig.get("cdaPath"), namespaces=namespace)
    assert validate_xml_value(xml_element=xml_elements[0], config_field=okconfig) == []

    config_no_text = {
        "fieldName": "biz",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:baz/test:biz",
        "textRequired": "True",
    }

    xml_elements = root.xpath(config_no_text.get("cdaPath"), namespaces=namespace)
    result = validate_xml_value(xml_elements[0], config_no_text)
    assert result == [
        "Field does not have a value. Field name: "
        + "'biz' Attributes: attribute #1: 'test'"
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
    assert validate_xml_value(xml_elements[0], config_text_matches_reg_ex) == []

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
    result = validate_xml_value(xml_elements[0], config_text_doesnt_match_reg_ex)
    assert result == [
        "The field value does not exist or doesn't match the following pattern: 'foo'."
        + " For the Field name: 'bar' value: 'test' Attributes: attribute #1: 'test'"
    ]

    config_text_not_required = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "foo",
    }
    xml_elements = root.xpath(
        config_text_doesnt_match_reg_ex.get("cdaPath"), namespaces=namespace
    )
    result = validate_xml_value(xml_elements[0], config_text_not_required)
    assert result == []


def test_get_ecr_custom_message():
    config_field_with_custom = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "foo",
        "customMessage": "this is a custom message",
    }
    result = _get_ecr_custom_message(
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
    result = _get_ecr_custom_message(
        config_field_no_custom, "this is a default message"
    )
    assert result == "this is a default message"


def test_get_xml_message_id():
    # parse and prep data from example file
    # for testing
    xml = sample_file_good_RR.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    parsed_ecr = etree.fromstring(xml, parser=parser)

    actual_result = _get_xml_message_id(
        parsed_ecr.xpath(EICR_MSG_ID_XPATH, namespaces=ECR_NAMESPACES)
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
        parsed_ecr.xpath(RR_MSG_ID_XPATH, namespaces=ECR_NAMESPACES)
    )
    assert actual_result == expected_result


def test_get_ecr_message_ids():
    # parse and prep data from example file
    # for testing
    xml = sample_file_good_RR.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    parsed_ecr = etree.fromstring(xml, parser=parser)

    actual_result = get_ecr_message_ids(parsed_ecr)
    expected_result = {
        "eicr": {
            "root": "2.16.840.1.113883.9.9.9.9.9",
            "extension": "db734647-fc99-424c-a864-7e3cda82e704",
        },
        "rr": {"root": "4efa0e5c-c34c-429f-b5de-f1a13aef4a28", "extension": None},
    }
    assert actual_result == expected_result

    xml = sample_file_good.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    parsed_ecr = etree.fromstring(xml, parser=parser)

    actual_result = get_ecr_message_ids(parsed_ecr)
    expected_result = {
        "eicr": {
            "root": "2.16.840.1.113883.9.9.9.9.9",
            "extension": "db734647-fc99-424c-a864-7e3cda82e704",
        },
        "rr": {},
    }
    assert actual_result == expected_result


def test_get_xml_element_details():
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
    result = get_xml_element_details(xml_elements[0], config_text_matches_reg_ex)
    assert result == (
        "Field name: 'bar' value: 'test' Attributes:"
        + " attribute #1: 'test' actual value: 'hello'"
    )

    result = get_xml_element_details(xml_elements[0], None)
    assert result == ""

    config_no_attrs = {
        "fieldName": "bar",
        "cdaPath": "//test:foo/test:bar",
        "textRequired": "True",
        "regEx": "test",
    }
    result = get_xml_element_details(xml_elements[0], config_no_attrs)
    assert result == "Field name: 'bar' value: 'test'"

    xml2 = (
        "<foo xmlns='test'><bar test='hello'></bar><baz><biz/></baz>"
        + "<biz>wrong</biz></foo>"
    )
    root2 = etree.fromstring(xml2)
    xml_elements2 = root2.xpath(
        config_text_matches_reg_ex.get("cdaPath"), namespaces=namespace
    )
    result = get_xml_element_details(xml_elements2[0], config_no_attrs)
    assert result == "Field name: 'bar'"

    config_no_text_required = {
        "fieldName": "bar",
        "attributes": [{"attributeName": "test"}],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "test",
    }
    result = get_xml_element_details(xml_elements[0], config_no_text_required)
    assert (
        result
        == "Field name: 'bar' Attributes: attribute #1: 'test' actual value: 'hello'"
    )


def test_get_xml_attributes():
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
    result = _get_xml_attributes(
        xml_elements[0], config_text_matches_reg_ex.get("attributes")
    )
    assert result == [
        "attribute #1: 'test' with the required value pattern: "
        + "'test' actual value: 'hello', attribute #2: 'foo'"
    ]

    result = _get_xml_attributes(xml_elements[0], None) == []


def test_validate_xml_related_element():
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
        _validate_xml_related_element(
            xml_elements[0],
            config.get("cdaPath"),
            config.get("relatives")[0],
        ).tag
        == "{test}baz"
    )
    result = _validate_xml_related_element(
        xml_elements[0],
        config.get("cdaPath"),
        config.get("relatives")[1],
    )
    assert result.tag == "{test}foo"

    result = _validate_xml_related_element(
        xml_elements[0],
        config.get("cdaPath"),
        config.get("relatives")[2],
    )
    assert result.tag == "{test}biz"

    result = _validate_xml_related_element(
        xml_elements[0],
        config.get("cdaPath"),
        config.get("relatives")[3],
    )
    assert result.tag == "{test}chaz"

    result = _validate_xml_related_element(
        xml_elements[0],
        config.get("cdaPath"),
        config.get("relatives")[4],
    )
    assert result is None

    result = _validate_xml_related_element(
        xml_elements[0],
        config.get("cdaPath"),
        config.get("relatives")[5],
    )
    assert result is None

    assert (
        _validate_xml_related_element(
            None,
            config.get("cdaPath"),
            config.get("relatives")[0],
        )
        is None
    )


def test_validate_xml_relatives():
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

    config_no_relatives = {
        "fieldName": "bar",
        "attributes": [
            {"attributeName": "test", "regEx": "test"},
            {"attributeName": "foo"},
        ],
        "cdaPath": "//test:foo/test:bar",
        "regEx": "test",
    }

    xml_elements = root.xpath(config.get("cdaPath"), namespaces=namespace)
    assert _validate_xml_relatives(xml_elements[0], config) is False
    assert _validate_xml_relatives(xml_elements[0], config_correct) is True
    assert _validate_xml_relatives(xml_elements[0], config_no_relatives) is True


def test_get_xml_relatives_details():
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

    assert _get_xml_relatives_details(None) == []
    assert _get_xml_relatives_details(config_correct["relatives"]) == [
        "Related elements:",
        "Field name: 'baz'",
        "Attributes:",
        "attribute #1: 'foo' with the required value pattern: 'bar'",
        "Field name: 'foo'",
        "Field name: 'biz'",
        "Field name: 'chaz'",
    ]
