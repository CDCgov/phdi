import uuid
from datetime import date
from unittest.mock import patch

import pytest
from app import utils
from app.phdc.builder import PHDCBuilder
from app.phdc.models import Address
from app.phdc.models import CodedElement
from app.phdc.models import Name
from app.phdc.models import Observation
from app.phdc.models import Organization
from app.phdc.models import Patient
from app.phdc.models import PHDCInputData
from app.phdc.models import Telecom
from lxml import etree as ET


@pytest.fixture
def phdc_input_data():
    return PHDCInputData(
        type="case_report",
        patient=Patient(
            name=[
                Name(
                    prefix="Mr.",
                    first="Jon",
                    middle="Aegon",
                    family="Targaryen",
                    type="official",
                ),
                Name(prefix="Mr.", first="Jon", family="Snow", type="pseudonym"),
            ],
            address=[
                Address(
                    type="Home",
                    street_address_line_1="123 Main Street",
                    city="Brooklyn",
                    postal_code="11201",
                    state="New York",
                ),
                Address(
                    type="workplace",
                    street_address_line_1="123 Main Street",
                    postal_code="55866",
                    city="Brooklyn",
                    state="New York",
                ),
            ],
            telecom=[
                Telecom(value="+1-800-555-1234"),
                Telecom(value="+1-800-555-1234", type="work"),
            ],
            administrative_gender_code="Male",
            race_code="2106-3",
            ethnic_group_code="2186-5",
            birth_time="09-09-1990",
        ),
        organization=[
            Organization(
                id="123456789",
                name="Scottish Rite Hospital",
                address=Address(
                    street_address_line_1="1001 Johnson Ferry Rd NE",
                    street_address_line_2="Ste 200",
                    city="Atlanta",
                    state="13",
                    postal_code="30034",
                    country="13089",
                ),
                telecom=Telecom(value="4047855252"),
            )
        ],
        clinical_info=[
            [
                Observation(
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="INV169",
                        code_system="2.16.840.1.114222.4.5.1",
                        display_name="Condition",
                    ),
                    value=CodedElement(
                        xsi_type="CE",
                        code="10274",
                        code_system="1.2.3.5",
                        display_name="Chlamydia trachomatis infection",
                    ),
                    translation=CodedElement(
                        xsi_type="CE",
                        code="350",
                        code_system="L",
                        code_system_name="STD*MIS",
                        display_name="Local Label",
                    ),
                )
            ],
            [
                Observation(
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="NBS012",
                        code_system="2.16.840.1.114222.4.5.1",
                        display_name="Shared Ind",
                    ),
                    value=CodedElement(
                        xsi_type="CE",
                        code="F",
                        code_system="1.2.3.5",
                        display_name="False",
                    ),
                    translation=CodedElement(
                        xsi_type="CE",
                        code="T",
                        code_system="L",
                        code_system_name="STD*MIS",
                        display_name="Local Label",
                    ),
                )
            ],
        ],
        social_history_info=[
            [
                Observation(
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="DEM127",
                        code_system="2.16.840.1.114222.4.5.232",
                        code_system_name="PHIN Questions",
                        display_name="Is this person deceased?",
                    ),
                    value=CodedElement(
                        xsi_type="CE",
                        code="N",
                        code_system_name="Yes/No Indicator (HL7)",
                        display_name="No",
                        code_system="2.16.840.1.113883.12.136",
                    ),
                    translation=CodedElement(
                        code="N",
                        code_system="2.16.840.1.113883.12.136",
                        code_system_name="2.16.840.1.113883.12.136",
                        display_name="No",
                    ),
                )
            ],
            [
                Observation(
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="NBS104",
                        code_system="2.16.840.1.114222.4.5.1",
                        code_system_name="NEDSS Base System",
                        display_name="Information As of Date",
                    ),
                    value=CodedElement(
                        xsi_type="TS",
                        value="20240124",
                    ),
                )
            ],
        ],
        repeating_questions=[
            [
                Observation(
                    obs_type="EXPOS",
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="DEM127",
                        code_system="2.16.840.1.114222.4.5.232",
                        code_system_name="PHIN Questions",
                        display_name="Is this person deceased?",
                    ),
                    value=CodedElement(
                        xsi_type="CE",
                        code="N",
                        code_system_name="Yes/No Indicator (HL7)",
                        display_name="No",
                        code_system="2.16.840.1.113883.12.136",
                    ),
                    translation=CodedElement(
                        code="N",
                        code_system="2.16.840.1.113883.12.136",
                        code_system_name="2.16.840.1.113883.12.136",
                        display_name="No",
                    ),
                )
            ],
            [
                Observation(
                    obs_type="EXPOS",
                    type_code="COMP",
                    class_code="OBS",
                    mood_code="EVN",
                    code=CodedElement(
                        code="NBS104",
                        code_system="2.16.840.1.114222.4.5.1",
                        code_system_name="NEDSS Base System",
                        display_name="Information As of Date",
                    ),
                    value=CodedElement(
                        xsi_type="TS",
                        value="20240124",
                    ),
                )
            ],
        ],
    )


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
def test_validate_phdc(phdc_input_data, validate_xml):
    builder = PHDCBuilder()
    builder.set_input_data(phdc_input_data)
    phdc = builder.build()
    phdc_output = phdc.to_xml_string()
    parsed_output = ET.fromstring(phdc_output.encode())
    assert validate_xml(parsed_output)
