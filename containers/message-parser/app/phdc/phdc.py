from lxml import etree as ET


class PHDC:
    def __init__(self, builder):
        self.header = builder.header


class PHDCBuilder:
    def __init__(self):
        self.header = None

    def _build_telecom(
        self,
        **kwargs: dict
        # phone: str,
        # use: Literal["HP", "WP", "MC"] = None,
    ):
        """
        Builds a `telecom` XML element for phone data including phone number (as
        `value`) and use, if available. There are three types of phone uses: 'HP'
        for home phone, 'WP' for work phone, and 'MC' for mobile phone.

        :param phone: The phone number.
        :param use: Type of phone number, defaults to None.
        :return: XML element of telecom data.
        """
        telecom_data = ET.Element("telecom")

        if "use" in kwargs.keys() and kwargs["use"] is not None:
            telecom_data.set("use", kwargs["use"])
        if "phone" in kwargs.keys() and kwargs["phone"] is not None:
            telecom_data.set("value", kwargs["phone"])

        return telecom_data

    def _build_addr(
        self,
        **kwargs
        # use: Literal["H", "WP"] = None,
        # line: str = None,
        # city: str = None,
        # state: str = None,
        # zip: str = None,
        # county: str = None,
        # country: str = None,
    ):
        """
        Builds an `addr` XML element for address data. There are two types of address
         uses: 'H' for home address and 'WP' for workplace address.

        :param use: Type of address, defaults to None.
        :param line: Street address, defaults to None.
        :param city: City, defaults to None.
        :param state: State, defaults to None.
        :param zip: Zip code, defaults to None.
        :param county: County, defaults to None.
        :param country: Country, defaults to None.
        :return: XML element of address data.
        """

        address_data = ET.Element("addr")
        if "use" in kwargs.keys() and kwargs["use"] is not None:
            address_data.set("use", kwargs["use"])

        for element, value in kwargs.items():
            if element != "use" and value is not None:
                if element == "line":
                    element = "streetAddressLine"
                elif element == "zip":
                    element = "postalCode"
                e = ET.Element(element)
                e.text = value
                address_data.append(e)

        return address_data

    def _build_name(
        self,
        **kwargs: dict
        # use: Literal["L", "P"] = None,
        # prefix: str = None,
        # given_name: Union[str, List[str]] = None,
        # last_name: str = None,
    ):
        """
        Builds a `name` XML element for address data. There are two types of name
         uses: 'L' for legal and 'P' for pseudonym.

        :param use: Type of address, defaults to None.
        :param prefix: Name prefix, defaults to None.
        :param given_name: String or list of strings representing given name(s),
          defaults to None.
        :param last_name: Last name, defaults to None.
        :return: XML element of name data.
        """

        name_data = ET.Element("name")
        if "use" in kwargs.keys() and kwargs["use"] is not None:
            name_data.set("use", kwargs["use"])

        for element, value in kwargs.items():
            if element != "use" and value is not None:
                if element == "given_name":
                    element = "given"

                    # Split single string names into first name and middle names as
                    # PHDC appears to only allow for up to two given names
                    if isinstance(value, str) and len(value.split()) > 1:
                        value = [
                            value.split()[0],
                            " ".join(v for v in (value.split()[1:])),
                        ]

                elif element == "last_name":
                    element = "family"

                # Append each value of a list, e.g., given name, as its own Element
                if isinstance(value, list):
                    value = [
                        value[0],
                        " ".join(v for v in (value[1:])),
                    ]
                    for v in value:
                        e = ET.Element(element)
                        e.text = v
                        name_data.append(e)
                else:
                    e = ET.Element(element)
                    e.text = value
                    name_data.append(e)

        return name_data

    def _build_custodian(
        self,
        id: str,
    ):
        """
        Builds a `custodian` XML element for custodian data, which refers to the
          organization from which the PHDC originates and that is in charge of
          maintaining the document.

        :param id: Custodian identifier.
        :return: XML element of custodian data.
        """
        if id is None:
            raise ValueError("The Custodian id parameter must be a defined.")

        custodian_data = ET.Element("custodian")
        assignedCustodian = ET.Element("assignedCustodian")
        representedCustodianOrganization = ET.Element(
            "representedCustodianOrganization"
        )

        id_element = ET.Element("id")
        id_element.set("extension", id)
        representedCustodianOrganization.append(id_element)

        assignedCustodian.append(representedCustodianOrganization)
        custodian_data.append(assignedCustodian)

        return custodian_data

    def _build_coded_element(self, element_name: str, **kwargs: dict):
        """
        Builds coded elements, such as administrativeGenderCode, using kwargs code,
          codeSystem, and displayName.

        :param element_name: Name of the element being built.
        :param code: The element code, defaults to None
        :param codeSystem: The element codeSystem that the code corresponds to, defaults
          to None
        :param displayName: The element display name, defaults to None
        :return: XML element of coded data.
        """
        element = ET.Element(element_name)

        for e, v in kwargs.items():
            if e != "element_name" and v is not None:
                element.set(e, v)
        return element

    def _build_patient(self, **kwargs: dict):
        patient_data = ET.Element("patient")

        for element, value in kwargs.items():
            if value is not None:
                if isinstance(value, ET._Element):
                    patient_data.append(value)
                elif element in [
                    "administrativeGenderCode",
                    "raceCode",
                    "ethnicGroupCode",
                ]:
                    # TODO: Determine how to implement std:raceCode and/or stdc:raceCode
                    v = self._build_coded_element(
                        element,
                        **{"displayName": value},
                    )
                    patient_data.append(v)
                else:
                    e = ET.Element(element)
                    e.text = value
                    patient_data.append(e)

        return patient_data

    def _build_recordTarget(
        self,
        **kwargs,
        # id: str,
        # root: str = None,
        # assigningAuthorityName: str = None,
        # telecom_data: str = None,
        # addr_data: str = None,
        # patient_data: str = None,
    ):
        """
        Builds a `recordTarget` XML element for recordTarget data, which refers to
          the medical record of the patient.

        :param id: recordTarget identifier
        :param root: recordTarget root
        :param assigningAuthorityName: recordTarget assigningAuthorityName
        :param telecom_data: XML data from _build_telecom
        :param addr_data: XML data from _build_addr
        :param patient_data: XML data from _build_patient

        :raises ValueError: recordTarget needs ID to be defined.

        :return recordTarget_data: XML element of the recordTarget
        """
        if "id" not in kwargs or kwargs["id"] is None:
            raise ValueError("The recordTarget id parameter must be a defined.")

        # create recordTarget element
        recordTarget_data = ET.Element("recordTarget")

        # Create and append 'patientRole' element
        patientRole = ET.Element("patientRole")
        recordTarget_data.append(patientRole)

        # initialize id data, add data, then append to patientRole
        id_element = ET.Element("id")
        id_element.set("extension", kwargs["id"])

        element_list = ["root", "assigningAuthorityName"]
        for id_elem in element_list:
            if id_elem in kwargs:
                id_element.set(id_elem, kwargs[id_elem])

        patientRole.append(id_element)

        # add address, telecom, patient
        element_methods = {
            "addr_data": self._build_addr,
            "telecom_data": self._build_telecom,
            "patient_data": self._build_patient,
        }

        for elem_key, method in element_methods.items():
            if elem_key in kwargs:
                element = method(**kwargs[elem_key])
                patientRole.append(element)

    def build(self):
        return PHDC(self)
