# Introduction
This file contains functionality and configuration descriptions for the IntakePipeline Azure function.

# Function App Settings
This function app module requires some config to be present. In production this is defined on the Function App Azure Resource in the Settings screen.  Locally, configuration is stored in `local.settings.json` under `Values`.

* Cloud Settings Documentation: https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings
* Local Settings Documentation: https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local#local-settings-file

The configuration values required to be set for the IntakePipeline function are described below.

* `INTAKE_CONTAINER_URL`: a container URL containing FHIR bundles (eg: https://pitestdatasa.blob.core.windows.net/bronze)\
    * Stored bundles must be of type `batch`.  Entries in the batch Bundle should contain a valid `request` describing how the `resource` should be submitted to the FHIR Server.
* `INTAKE_CONTAINER_PREFIX`: a string prefix so we're not scanning the entire container (eg: decrypted/valid-messages/)\
    * Assuming prefixes are a complete directory path, prefixes should have a trailing /.  Also, there must be a sub-structure of record types (all caps) under the prefix (eg: decrypted/valid-messages/VXU).
* `INVALID_OUTPUT_CONTAINER_PATH`: the blob container path to store invalid messages that could not be processed.
* `VALID_OUTPUT_CONTAINER_PATH`: the blob container path to store processed items.
* `SMARTYSTREETS_AUTH_ID`: an auth id used in geocoding
* `SMARTYSTREETS_AUTH_TOKEN`: the corresponding auth token
* `HASH_SALT`: a salt to use when hashing the patient identifier
* `FHIR_URL`: the base url for the FHIR server used to persist FHIR objects

# Building Blocks
The IntakePipeline Azure Function orchestrates a series of actions, implemented in discrete Python building blocks, each of which is described below.  

## Conversion
The conversion building block is responsible for converting from a raw input format (HL7 Version 2, or CCD) to FHIR.  This includes normalization as well as conversion of batch files and messages.

### Convert batch to list
A batch file containing one or more messages is converted into a list of inidivdual messages.  Prior to conversion, the following normalization is applied:

*Delimiter Normalization*
* Windows-style delimiters (CR-LF) are replaced with Unix-style delimiters (LF).
* Unicode characters vertical tab (\u000b) and file separator (\u001c) delimiters between messages are removed.

After performing the normalization described above, content from the input batch file containing 1 or more messages is divided into a list of messages.  Input is expected to be HL7v2.  Batch headers and trailers (FHS, BHS, BTS, FTS) are ignored, and each individual message is expected to begin with an MSH segment.

### Convert message to FHIR
An HL7 or CCDA message is converted to FHIR.  Prior to conversion, it passes through an initial cleansing step, which peforms datetime normalization described below.

Some systems send a higher level of precision in HL7 datetime fields than is allowed by the HL7 standard.  
HL7 specifies maximum precision for:

* Base datetime = 14
* Fractional Seconds = 4
* Timezone Offset = 4


Specifying a higher level of precision  can cause problems during downstream processing.  Assuming datetimes are in the following format, normalization truncates precision beyond the maxiumum allowed by HL7.

`BaseDatetime[.FractionalSeconds][+/-TimezoneOffset]`

The following HL7 datetime fields are normalized.
* MSH-7 Message date/time
* PID-7 Date of Birth
* PID-29 Date of Death
* PID-33 Last update date/time
* PV1-44 Admisstion Date
* PV1-45 Discharge Date
* ORC-9 Date/time of transaction
* ORC-15 Order effective date/time
* ORC-27 Filler's expected availability date/time
* OBR-7 Observation date/time
* OBR-8 Observation end date/time
* OBR-22 Status change date/time
* OBR-36 Scheduled date/time
* OBX-12 Effective date/time of reference range
* OBX-14 Date/time of observation
* OBX-19 Date/time of analysis
* TQ1-7 Start date/time
* TQ1-8 End date/time
* SPM-18 Specimen received date/time
* SPM-19 Specimen expiration date/time
* RXA-3 Date/time start of administration
* RXA-4 Date/time end of administration
* RXA-16 Substance expiration date
* RXA-22 System entry date/time

After performing normalization described above, the Azure FHIR Converter is used to convert the normalized message to FHIR.

The [Azure FHIR converter](https://docs.microsoft.com/en-us/azure/healthcare-apis/fhir/convert-data) uses [Liquid templating engine](https://shopify.github.io/liquid/) to convert both HL7 and CCDA messages to FHIR.

For detailed information about mapping and transformation to FHIR, you can review the appropriate Liquid templates.  Follow the links to the GitHub template store:
* Case Reports: [CCD](https://github.com/microsoft/FHIR-Converter/blob/main/data/Templates/Ccda/CCD.liquid)
* Immunizations: [VXU_V04](https://github.com/microsoft/FHIR-Converter/blob/main/data/Templates/Hl7v2/VXU_V04.liquid)
* Lab Results: [ORU_R01](https://github.com/microsoft/FHIR-Converter/blob/main/data/Templates/Hl7v2/ORU_R01.liquid)

### Transform
The transform building block is responsible for standardizing data field formatting.
#### Transform Names
Names are standardized by applying the following modifications:
* Remove numeric digits
* Trim whitespace
* Make all-caps

#### Transform Phone Numbers
Phone numbers are standardized by applying the following modifications:
* Remove non-numeric digits
* Filter phone numbers that are not exactly 10 digits long

#### Transform Address
Addresses are standardized by making a lookup request to the SmartySheets API.  The request includes address lines, city, state, and postal code.  If a geocoded result is returned, the address is replaced with the geocoded result.  Longitude and latitude is also added as a FHIR extension.  If no geocoded result is found, the original remains, untransformed.

### Linkage
The linkage building block is responsible for grouping information for the same patient across different messages and data sources.

#### Master Identifier Generation
A master patient identifier is generated using a salted SHA-256 hash of the standardized patient name, birthdate and address.  The master patient identifier is added to the identifier array in the FHIR Patient resource.  

### FHIR Server Storage
The FHIR Server building block is responsible for uploading resources to the FHIR server.

#### Upload to FHIR Server
A [batch FHIR bundle](https://www.hl7.org/fhir/bundle.html#transaction) is submitted via HTTP POST to the configured FHIR server.

### Blob Storage
The Blob Storage building block is responsible for storing FHIR bundles for successfully processed messages to Blob storage.  Messages that failed to process successfully may be stored to a different blob location.

#### Generate Blob Name
Blob names are formatted as:
`<Base Filename>-<Message Index>`
The _"Base Filename"_ is the original filename without the file type suffix (ELR_YYYYMMDD_i.hl7 becomes ELR_YYYYMMDD_i).  Since input files may contain batches of multiple messages, the _"Message Index"_ is the zero-based index of the message within that file.

#### Store Blob
Blobs are stored according to the configured container URL and locations.