# Tutorials: The FHIR Conversion Module

This guide serves as a tutorial overview of the functionality available in `phdi.fhir.conversion`. It will cover concepts such as using a credential manager, what data types are allowed, and what error messages may be returned. 

## Why Convert to FHIR?
In the design of our building blocks, we have modules to be used specifically with the FHIR data type. 

FHIR is a widely used standard designed for storing and interacting with healthcare data. There is significant overlap between healthcare and public health domains. In addition, FHIR standard maintainers have focused on keeping the FHIR data format general so it can be applied to areas like public health. Primary goals of promoting a common format like FHIR include allowing the PHDI tools to help a wider array of public health agencies, and facilitating inter-agency data exchange.

## Pre-requisites
Currently, the solution depends on an Azure FHIR Server instance to convert HL7 v2 or CCDA to FHIR. 

## The Basics: How to Convert
This package contains the process of converting HL7 v2 or CCDA into FHIR (JSON). As a part of our library, we encourage the use of the FHIR data type for all of our functions. This package aims to help easily convert other common healthcare data formats to FHIR. 

With a valid HL7 v2 message, you can pass in the data to the `convert_to_fhir` function as a string. 

In addition to an HL7 v2 message, you need to have a FHIR server and credential manager set up.

Ensure that you are logged in to Azure so that your credentials are recognized by the credential manager. For more information, see cloud-tutorial.md 

```python
from phdi.fhir.conversion import convert_to_fhir

message = """MSH|^~\&|ADT1|GOOD HEALTH HOSPITAL|GHH LAB, INC.|GOOD HEALTH HOSPITAL|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||
EVN|A01|200708181123||
PID|1||PATID1234^5^M11^ADT1^MR^GOOD HEALTH HOSPITAL~123456789^^^USSSA^SS||EVERYMAN^ADAM^A^III||19610615|M||C|2222 HOME STREET^^GREENSBORO^NC^27401-1020|GL|(555) 555-2004|(555)555-2004||S||PATID12345001^2^M10^ADT1^AN^A|444333333|987654^NC|
NK1|1|NUCLEAR^NELDA^W|SPO^SPOUSE||||NK^NEXT OF KIN
PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A|||SUR||||ADM|A0|"""

url = "https://azure_fhir_url.com"

cred_manager = AzureCredentialManager(url)
convert_to_fhir(message, cred_manager, url)
>>>{...converted fhir version of the the HL7 v2...}
```

After using the `convert_to_fhir` method, you will have your data in FHIR format