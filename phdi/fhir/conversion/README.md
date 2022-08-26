# FHIR Conversion

FHIR Conversion helps convert HL7 v2 or CCDA (XML) data into FHIR (JSON) data. Our library works well with FHIR so this package helps bridge the gap between other healthcare data types and FHIR. A message is passed and the `convert_to_fhir` function determines what type of data is passed, then converts the data to FHIR. 