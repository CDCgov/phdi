# Architecture of the FHIR to PHDC Conversion Process
This document outlines the architectural details that make up the FHIR to PHDC conversion process.

## Overview
The DIBBs Message Parser Service provides an automated, config-driven way to parse data elements from a given FHIR bundle. The FHIR to PHDC conversion builds on this service by converting the message parser output data into Public Health Document Container (PHDC) XML files. The conversion process works by parsing data from FHIR bundles and organizing the parsed data into dataclasses that make up input data for the PHDC builder. The builder uses the input data to construct each section of the PHDC. The builder can create the header, Social History Information, Clinical Information, and Repeating Questions sections of a PHDC Case Report.

### Parsing FHIR Bundles for Conversion to PHDC
In the first step of the FHIR to PHDC conversion process, the Message Parsing Service applies a schema to a given FHIR bundle and outputs a `parsed_values` dictionary. The `phdc_case_report_schema.json` parses information about the patient, custodian organization, author, and observations and roughly sorts each piece of information into the appropriate sections of the PHDC, e.g., data from a Composition FHIR resource is parsed into the `custodian_represented_custodian_organization` section because the Composition information will end up in the Custodian section of the PHDC.

In the case of observations the sorting is taken one step further. The secondary schema parses the data and roughly sorts it into the subsections of the observation element that they will appear in within the PHDC. PHDC observations have two primary subsections - code and value - and an optional translation subsection. Each subsection has a code, codeSystem, codeSystemName, and displayName component. In order to ensure that the code subsection has the appropriate codeSystem, i.e., is not assigned the codeSystem from the value subsection, the parsed values are prefixed with their corresponding subsection. That is, the parsed `code_code_system` corresponds to the codeSystem component in the code subsection and `value_code_system` corresponds to the codeSystem in the value subsection.


```
<observation classCode="OBS" moodCode="EVN">
  <code 
    code="INV169" 
    codeSystem="2.16.840.1.114222.4.5.232"           
    codeSystemName="PHIN Questions" 
    displayName="Condition">
  </code>
  <value 
    code="10190" 
    codeSystem="2.16.840.1.114222.4.5.277"
    codeSystemName="Notifiable Event Code List" 
    displayName="Pertussis"
    xsi:type="CE">
  </value>
</observation>

```


### Transforming Parsed Values into PHDCInputData
Once the Message Parser Service returns the data as the dictionary, `parsed_values`, the next step is transforming the parsed values into PHDCInputData dataclass. The transformation consists of organizing the parsed values into the internal dataclasses of the PHDCInputData, e.g., Address, Name, Telecom, Patient, Organization, or Observation. 

The transformation step is important for divvying up the parsed observations into the appropriate section of the PHDC. In the parsing step, all observation resources are grouped under “observations” in `parsed_values`. In a PHDC, however, observations appear in three places: the Social History Information, Clinical Information, and Repeating Questions sections. The transformation step uses the `obs_type` (if present) to sort the observations into the appropriate observation group. Further, the transformation step ensures that all observation components are grouped together as a list of Observations. 

### Building PHDC
The PHDCBuilder uses the PHDCInputData to construct the required sections of a PHDC. 

1. The builder constructs the base PHDC, which consists of XML namespace attribute declarations and establishes the PHDC root element as `Clinical Document`.
2. The builder constructs the PHDC header section, which consists of elements relating to the creation and transmission of the PHDC, such as the RecordTarget and Custodian information. 
3. The construction of the PHDC body section depends on the PHDC type. For Case Report type, the builder will construct Social History Information, Clinical Information, and Repeating Questions sections for the body. 

Within the body construction, the Social History Information and Clinical Information sections are built very similarly while the Repeating Questions section has some additional nuance to its construction. All three body sections begin with adding the appropriate component information, e.g., section title. Next, Social History and Clinical Information add observations from the PHDCInputData to their respective sections while Repeating Questions adds each observation within a list of Observations to an Organizer subsection that is nested in Repeating Questions. 
