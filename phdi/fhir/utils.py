import logging
import re
import hl7

from typing import List, Dict
import xml.etree.ElementTree as et

import requests


def convert_to_fhir():
    pass


def _get_fhir_conversion_settings(message: str):

    try:
        root = et.fromstring(message)
        if "ClinicalDocument" in root.tag:
            root_template = "CCD"
            input_data_type = "Ccda"
            template_collection = "microsofthealth/ccdatemplates:default"

            for child in root:
                if (
                    "code" in child.tag
                    and child.get("codeSystem") == "2.16.840.1.113883.6.1"
                ):
                    break

            print(child.attrib)
    except:
        pass


url = "https://raw.githubusercontent.com/HL7/C-CDA-Examples/master/Documents/Procedure%20Note/Procedure_Note.xml"
resp = requests.get(url)
msg = resp.content
_get_fhir_conversion_settings(msg)
