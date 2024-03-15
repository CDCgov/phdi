## Getting Started with the DIBBs TEFCA Viewer

### Introduction
The DIBBs TEFCA Viewer offers a proof-of-concept service for users to query health information networks as part of their case investigation work. The Trusted Exchange Framework and Common Agreement (TEFCA) describe the high-level principles that networks should adhere to for trusted exchange as well as the legal agreement enabling network-to-network data sharing. The goal of TEFCA is to enable the exchange of electronic health information across different health information networks. The TEFCA Viewer provides users a free, light-weight method for trying out specific queries that public health agencies might need for high-priority case investigations. 

The TEFCA Viewer is available at [DIBBs TEFCA Viewer](https://dibbs.cloud/tefca-viewer/patient-search). Users may specify the FHIR server, the use case, and patient demographic information in their query. See below for specific queries using synthetic data. After filling in the query infrmation and hitting the `Submit` button, the `Query Response` section will return the appropriate data for the specified user case as a FHIR bundle. 

Users may choose from the following query information:
1. FHIR Server
    * Meld: a server of synthetic data from the Interoperability Institute 
    * eHealth Exchange: a TEFCA-certified Qualified Health Information Exchange Network (QHIN)
2. Use Case 
    * Newborn Screening
    * Syphilis
    * Social Determinants of Health

### Example Queries
These queries will successfully return synthetic patient data. All other queries will return a `"No patients found. Please refine your search."` error.

1. Newborn Screening Use Case
    * FHIR Server: eHealth Exchange
    * Use Case: Newborn Screening
    * First Name: Cucumber
    * Last Name: Hill
    * Date of Birth: 08/29/2023

2. Syphilis Use Case
    * FHIR Server: Meld
    * Use Case: Syphilis
    * First Name: Veronica
    * Last Name: Blackstone
    * Date of Birth: 06/18/1998

3. Social Determinants of Health Use Case
    * FHIR Server: Meld
    * Use Case: Syphilis
    * First Name: Veronica
    * Last Name: Blackstone
    * Date of Birth: 06/18/1998

