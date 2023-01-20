# PRIME Public Health Data Infrastructure
[![Test github badge](https://github.com/CDCgov/phdi/actions/workflows/test.yaml/badge.svg)](https://github.com/CDCgov/phdi/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/CDCgov/phdi/branch/main/graph/badge.svg)](https://codecov.io/gh/CDCgov/phdi)
- [PRIME Public Health Data Infrastructure](#prime-public-health-data-infrastructure)
  - [Getting Started](#getting-started)
    - [How to import PHDI](#how-to-import-phdi)
  - [Overview](#overview)
    - [Problem Scope](#problem-scope)
  - [Standard Notices](#standard-notices)
    - [Public Domain Standard Notice](#public-domain-standard-notice)
    - [License Standard Notice](#license-standard-notice)
    - [Privacy Standard Notice](#privacy-standard-notice)
    - [Contributing Standard Notice](#contributing-standard-notice)
    - [Records Management Standard Notice](#records-management-standard-notice)
    - [Related documents](#related-documents)
    - [Additional Standard Notices](#additional-standard-notices)

**General disclaimer** This repository was created for use by CDC programs to collaborate on public health related projects in support of the [CDC mission](https://www.cdc.gov/about/organization/mission.htm). GitHub is not hosted by the CDC, but is a third party website used by CDC and its partners to share information and collaborate on software. CDC use of GitHub does not imply an endorsement of any one particular service, product, or enterprise.

## Getting Started

In order to use the PHDI Building Blocks library, you need [Python 3.9 or higher](https://www.python.org/downloads/) and [pip python package manager](https://pip.pypa.io/en/stable/installation/) (or any python package manager)


To install using pip:
```
pip install phdi
```

### How to import PHDI

Our project is split up into two parts. Our FHIR supporting version and our generic version.

Example import for FHIR:
```
 from phdi.fhir.geospatial.census import CensusFhirGeocodeClient
```

Example import for generic:
```
 from phdi.geospatial.census import CensusGeocodeClient
```

Every building block has a FHIR counterpart that works well with FHIR bundles as inputs. The generic version is used for all other non-FHIR inputs.

For further information on the tutorial: [Geospatial Tutorial](tutorials/geospatial-tutorial.md)

## Overview

The PRIME Public Health Data Infrastructure projects are part of the Pandemic-Ready Interoperability Modernization Effort, a multi-year collaboration between CDC and the U.S. Digital Service (USDS) to strengthen data quality and information technology systems in state and local health departments.

This repository contains source code for a platform to help state, tribal, local and territorial (STLT) public health departments ingest and report on public health data.  It contains the following components:

- **Data Ingestion** - Data ingestion tools provide a common framework to prepare data for storage, and store the data in a common standard data model ([FHIR](https://hl7.org/FHIR/)). 
  - __Harmonization__ - Data harmonization tools can operate on raw input data (HL7 version 2, CCDA) and convert to the common data model format (FHIR).
  - __Geospatial__ - Geospatial tools provide a common interface for obtaining precise geographic locations based on street addresses from input data.
  - __Linkage__ - Linkage tools assign a common identifier to patient records to link and deduplicate patients seen across data contributors.
  - __Transport__ - Transport tools provide a mechanism to store and interact with data stored to a central repostory (FHIR server). 
- **Reporting** - Reporting tools define a dynamic framework for building custom data models in an analysis-ready output format.
  - __Tabulation__ - Tabulation provides tools to retrieve data dynamically-defined records and data fields from the common data platform (FHIR server), extract, convert it to a tabular representation, and store to a user-defined tabular storage file type (Parquet or CSV).
- **Implementation Support** - Implemetnation resources support implementing STLTs to configure a PHDI-driven workflow to manage their data and analysis workflows.
  - __Cloud-agnostic tools__ - A common PHDI programming interface supports STLTs interacting with cloud-based data storage (containers/buckets), and FHIR servers in a common way.
  - __Examples and Tutorials__ - Example and tutorial materials help STLTs implement the PHDI solution more quickly by providing easy-to-follow examples and tutorials.

The PRIME Public Health Data Infrastructure prototype a sibling project to [PRIME ReportStream](https://reportstream.cdc.gov), focusing on delivering COVID-19 test data to public health departments, and [PRIME SimpleReport](https://simplereport.gov), working on a better way to report COVID-19 rapid tests.

### Problem Scope

Long-term Vision: Current public health systems to digest, analyze, and respond to data are siloed. Lacking access to actionable data, our national, as well as state, local, and territorial infrastructure, isn’t pandemic-ready. Our objective is to help the CDC best support STLTs in moving towards a modern public health data infrastructure.

## Additional Acknowledgments 

The compiled database mappings of root names to various nicknames was produced by the aggregation and synthesis of open source work from a number of projects. While we do not employ the packages and wrappers used by the various projects (merely their open source data), we do wish to give credit to their various works building collections of nickname mappings. These projects are:

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
