# Overview

The DIBBs [message parser](https://github.com/CDCgov/phdi/tree/main/containers/message-parser) offers a flexible config-driven solution for extracting data elements of interest from FHIR via FHIRPath. This set of code adds PHDC as an alternate output format to the message parser to convert data received from FHIR to PHDC.

Once complete, with this code, there will be a parsing config file for PHDC such that when a client makes a request to the message parser with a FHIR bundle that calls for using the PHDC parsing config, then the message parser will extract the required data from FHIR, construct a PHDC XML, and return that file to the client.

## Purpose

In order to support the exchange of data from a non-NBS jurisdiction to an NBS jurisdiction, data needs to be able to be converted from FHIR to Public Health Document Container (PHDC), the interface specification implemented by NBS.

More broadly offering FHIR to PHDC creates a mechanism for NBS to handle the ingestion of FHIR data which offers a significant step forward in terms of furthering interoperability between surveillance systems.

## Code (WIP)

### [phdc.py](https://github.com/CDCgov/phdi/blob/main/containers/message-parser/app/phdc/phdc.py)

This program initializes the `PHDCBuilder` Class, which is intended to take a json-formatted message from `message_parser`'s PHDC formatted json message and transform it into a PHDC-compliant XML file.
