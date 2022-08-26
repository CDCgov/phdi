# Tutorials: The FHIR Conversion Module

This guide serves as a tutorial overview of the functionality available in `phdi.fhir.conversion`. It will cover concepts such as using a credential manager, what data types are allowed, and what error messages may be returned. 

## Why Convert to FHIR?
In the design of our building blocks, we have modules to be used specifically with the FHIR data type. 

## The Basics: How to Convert
This package contains the process of converting HL7 v2 or CCDA into FHIR (JSON). As a part of our library, we encourage the use of the FHIR data type for all of our functions. This package aims to help easily convert other common healthcare data formats to FHIR. 

Suppose you had an HL7 data that looked like the example below:
```
MSH|^~\&|ADT1|GOOD HEALTH HOSPITAL|GHH LAB, INC.|GOOD HEALTH HOSPITAL|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||
EVN|A01|200708181123||
PID|1||PATID1234^5^M11^ADT1^MR^GOOD HEALTH HOSPITAL~123456789^^^USSSA^SS||EVERYMAN^ADAM^A^III||19610615|M||C|2222 HOME STREET^^GREENSBORO^NC^27401-1020|GL|(555) 555-2004|(555)555-2004||S||PATID12345001^2^M10^ADT1^AN^A|444333333|987654^NC|
NK1|1|NUCLEAR^NELDA^W|SPO^SPOUSE||||NK^NEXT OF KIN
PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A|||SUR||||ADM|A0|
```

With a valid HL7 v2 message, you can pass in the data to the `convert_to_fhir` function as a string. 

In addition to an HL7 v2 message, you need to have a FHIR server and credential manager set up.


```
from phdi.fhir.conversion import convert_to_fhir

message = "...the HL7 data above..."
settings = _get_fhir_conversion_settings(message)
assert settings == {
    "root_template": "ADT_A01",
    "input_data_type": "HL7v2",
    "template_collection": "microsofthealth/fhirconverter:default",
}
```