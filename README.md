# PRIME Public Health Data Infrastructure (PHDI)
[![codecov](https://codecov.io/gh/CDCgov/phdi/branch/main/graph/badge.svg)](https://codecov.io/gh/CDCgov/phdi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Test github badge](https://github.com/CDCgov/phdi/actions/workflows/test.yaml/badge.svg)](https://github.com/CDCgov/phdi/actions/workflows/test.yaml)
- [PRIME Public Health Data Infrastructure (PHDI)](#prime-public-health-data-infrastructure-phdi)
  - [Overview](#overview)
    - [Problem Scope](#problem-scope)
  - [Getting Started](#getting-started)
  - [Main Features](#main-features)
  - [Where to Get PHDI](#where-to-get-phdi)
  - [Documentation](#documentation)
  - [Additional Acknowledgments](#additional-acknowledgments)
  - [Standard Notices](#standard-notices)
    - [Public Domain Standard Notice](#public-domain-standard-notice)
    - [License Standard Notice](#license-standard-notice)
    - [Privacy Standard Notice](#privacy-standard-notice)
    - [Contributing Standard Notice](#contributing-standard-notice)
    - [Records Management Standard Notice](#records-management-standard-notice)
    - [Related documents](#related-documents)
    - [Additional Standard Notices](#additional-standard-notices)

**General disclaimer** This repository was created for use by CDC programs to collaborate on public health related projects in support of the [CDC mission](https://www.cdc.gov/about/organization/mission.htm). GitHub is not hosted by the CDC, but is a third party website used by CDC and its partners to share information and collaborate on software. CDC use of GitHub does not imply an endorsement of any one particular service, product, or enterprise.

## Overview

This repository is a part of the CDC/USDS [PHDI project](https://cdcgov.github.io/phdi-site/) and has two components: 
1. PHDI Python Package
2. PHDI containerized Building Blocks 

The PHDI Python package contains source code for a platform to help public health authorities (PHAs) ingest and report on public health data. This platform is composed of **Building Blocks**, which are modular software tools that, when composed together, can improve data quality and reduce data cleaning workloads by providing analysis-ready data to downstream public health surveillance systems and other analytical and reporting applications. 

PHDI contains: 
- Our SDK — the Python library containing Building Block source code
  - [Repository](https://github.com/CDCgov/phdi/tree/main/phdi)
  - [API documentation](https://cdcgov.github.io/phdi/latest/sdk/phdi.html)
- Containerized web services exposing Building Block functionality as HTTP endpoints
  - [Repository](https://github.com/CDCgov/phdi/tree/main/containers)
  - [User guide](https://cdcgov.github.io/phdi/) (under Building Blocks)
- Cloud Starter Kit — Repositories that implement a complete cloud-based pipeline composed of Building Blocks
  - [Azure](https://github.com/CDCgov/phdi-azure)
  - [Google Cloud Platform](https://github.com/CDCgov/phdi-google-cloud)

### Problem Scope

Current public health systems that digest, analyze, and respond to data are siloed. Lacking access to actionable data, our national, as well as state, local, and territorial infrastructure, isn’t pandemic-ready. Our objective is to help the CDC best support PHAs in moving towards a modern public health data infrastructure. See our [public website](https://cdcgov.github.io/dibbs-site/) for more details.

PHDI is a sibling project to [PRIME ReportStream](https://reportstream.cdc.gov), which focuses on improving the delivery of COVID-19 test data to public health departments, and [PRIME SimpleReport](https://simplereport.gov), which provides a better way for organizations and testing facilities to report COVID-19 rapid tests to public health departments.

## Getting Started

In order to use the PHDI library, you need [Python 3.9 or higher](https://www.python.org/downloads/) and [pip python package manager](https://pip.pypa.io/en/stable/installation/) (or any python package manager).

To install using pip:
```
pip install phdi
```

## Main Features

Here are the current tools that PHDI offers:
- **Containerized Building Blocks**
  -   **[Alerts](https://cdcgov.github.io/phdi/latest/containers/alerts.html)** - Provides the ability to send alerts via SMS, Slack, or Microsoft Teams
  -   **[FHIR Converter](https://cdcgov.github.io/phdi/latest/containers/fhir-converter.html)** - Enables conversion of health data from legacy formats (e.g., HL7 version 2, CCDA) to [FHIR](https://hl7.org/FHIR/), a standard for health care data exchange
  -   **[Data Ingestion](https://cdcgov.github.io/phdi/latest/containers/ingestion.html)** - Includes the entire pipeline of Building Blocks below
      -  **[Harmonization](https://cdcgov.github.io/phdi/latest/containers/ingestion.html#tag/fhirharmonization)** - Standardizes input data (e.g., patient names and phone numbers) to streamline the process of cleaning data and improve data quality
      - **[Geospatial](https://cdcgov.github.io/phdi/latest/containers/ingestion.html#tag/fhirgeospatial)** - Provides a common interface for obtaining precise geographic locations based on street addresses from input data
      - **[Linkage](https://cdcgov.github.io/phdi/latest/containers/ingestion.html#tag/fhirlinkage)** - Assigns a common identifier to patient records in order to link and deduplicate patient records seen across data contributors
      - **[Transport](https://cdcgov.github.io/phdi/latest/containers/ingestion.html#tag/fhirtransport)** - Offers functionality for reading and writing data from storage resources (e.g,. FHIR servers)  
  -   **[Message Parser](https://cdcgov.github.io/phdi/latest/containers/message-parser.html)** - Extracts desired fields from a given message
  -   **[Tabulation](https://cdcgov.github.io/phdi/latest/containers/tabulation.html)** - Extracts data from a FHIR server, converts it to a tabular representation, and stores it to a user-defined tabular storage file type (e.g., Parquet or CSV)
  -   **[Record Linkage](https://cdcgov.github.io/phdi/latest/containers/record-linkage.html)** - Links new health care messages to existing records if a connection exists
  -   **[Validation](https://cdcgov.github.io/phdi/latest/containers/validation.html)** - Checks whether health care messages are in the proper format and contain user-defined fields of interest 
- **Implementation Support** - Resources to help users implement PHDI tools to manage their data and analysis workflows
  - **[Examples](https://github.com/CDCgov/phdi/tree/main/examples)** - Sample data that simulates how a Building Block could be used 
  - **[Tutorials](https://github.com/CDCgov/phdi/tree/main/tutorials)** - Step-by-step instructions to implement Building Blocks source code

## Where to Get PHDI 

The source code is hosted on GitHub at: https://github.com/CDCgov/phdi.

The latest released version is available at the [Python Package Index (PyPI)](https://pypi.org/project/phdi/).

**Python modules**
```
pip install phdi
```

**Containerized services**
```
build from source
build Docker locally
pull down Docker images from GitHub
```

## Documentation

PHDI documentation is currently hosted on GitHub Pages: https://cdcgov.github.io/phdi/ 

There, you can find our: 
- SDK API reference documentation
- User guide for containerized Building Blocks

## Additional Acknowledgments 

We mapped the rootnames of the PHDI database to nicknames produced by the aggregation and synthesis of open source work from a number of projects. While we do not employ the packages and wrappers used by the various projects (merely their open source data), we wish to give credit to their various works building collections of nickname mappings. These projects are:

* [Secure Enterprise Master Patient Index](https://github.com/MrCsabaToth/SOEMPI), based on OpenEMPI, conducted by Vanderbilt University
* [Curated Nicknames](https://github.com/carltonnorthern/nicknames), scraped from genealogy webpages and run by Old Dominion University Web Science and Digital Libraries Research Group
* [Simple Public Domain Nickname Mappings](https://github.com/onyxrev/common_nickname_csv), hand collected using various sources
* [Lingua En Nickname](https://github.com/brianary/Lingua-EN-Nickname), collected from a series of GenWeb projects
* [diminutives.db](https://github.com/HaJongler/diminutives.db), compiled via a nickname extract using Wikipedia and Wiktionary

## Standard Notices

### Public Domain Standard Notice

This repository constitutes a work of the United States Government and is not
subject to domestic copyright protection under 17 USC § 105. This repository is in
the public domain within the United States, and copyright and related rights in
the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this repository will be released under the CC0 dedication. By
submitting a pull request you are agreeing to comply with this waiver of
copyright interest.

### License Standard Notice

This project is in the public domain within the United States, and copyright and
related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this project will be released under the CC0 dedication. By
submitting a pull request or issue, you are agreeing to comply with this waiver
of copyright interest and acknowledge that you have no expectation of payment,
unless pursuant to an existing contract or agreement.

### Privacy Standard Notice

This repository contains only non-sensitive, publicly available data and
information. All material and community participation is covered by the
[Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md)
and [Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
For more information about CDC's privacy policy, please visit [http://www.cdc.gov/other/privacy.html](https://www.cdc.gov/other/privacy.html).

### Contributing Standard Notice

Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo)
and submitting a pull request. (If you are new to GitHub, you might start with a
[basic tutorial](https://help.github.com/articles/set-up-git).) By contributing
to this project, you grant a world-wide, royalty-free, perpetual, irrevocable,
non-exclusive, transferable license to all users under the terms of the
[Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or
later.

All comments, messages, pull requests, and other submissions received through
CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for more information.

### Records Management Standard Notice

This repository is not a source of government records, but is a copy to increase
collaboration and collaborative potential. All government records will be
published through the [CDC web site](http://www.cdc.gov).

### Related documents

- [Open Practices](docs/open_practices.md)
- [Rules of Behavior](docs/rules_of_behavior.md)
- [Disclaimer](docs/DISCLAIMER.md)
- [Contribution Notice](docs/CONTRIBUTING.md)
- [Code of Conduct](docs/code-of-conduct.md)

### Additional Standard Notices

Please refer to [CDC's Template Repository](https://github.com/CDCgov/template)
for more information about [contributing to this repository](https://github.com/CDCgov/template/blob/master/CONTRIBUTING.md),
[public domain notices and disclaimers](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md),
and [code of conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
