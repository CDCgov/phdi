# PHDI Geocoding Pilot Partnership 2022 

# Pilot Overview
## What are Building Blocks, and why do they matter?

The Center for Disease Control’s **Data Modernization Initiative (DMI)** is a multi-year effort to [modernize core public health data and surveillance infrastructure across the federal and state public health landscape](https://www.cdc.gov/surveillance/projects/dmi-initiative/index.html). Its goal is to create *resilient*, *adaptable,* *sustainable,* and *real-time* public health data systems to protect against public health threats, and ultimately be “response-ready”. 
As a part of that initiative, the CDC and Office of the National Coordinator for Health Information Technology (ONC) are collaborating on a **North Star Architecture** that helps with alignment on a shared vision for public health data infrastructure for states, territories, localities, and jurisdictions. 
**Building Blocks** allow us to move towards that North Star Architecture by taking what was once siloed, isolated, brittle, slow, and maladapted, and transform it into something connected, expeditious, adaptable, flexible, and most of all, high-quality. This open-source ecosystem consists of easily shareable data streams that public health practitioners can use. Specifically, **Building Blocks** are ****modular software services that each accomplish one specific task and that can be combined to create larger data ingestion, processing and analysis pipelines. 

## What is the Geocoding Building Block?

**The Geocoding Building Block** creates tools for mapping geospatial data to its canonical representation for purposes of standardization, validation, cleaning, and/or enrichment. This Building Block is available as a module in the `phdi` [Python SDK](https://github.com/CDCgov/phdi). This SDK creates a standardized library where users can geocode an individual address or multiple addresses within a FHIR bundle. The current functionality supports standardizing addresses in a variety of input formats and enriching data with latitude and longitude. Read through the [Geospatial Tutorial](https://github.com/CDCgov/phdi#getting-started) for more detail about using the geospatial module. 

## What are the objectives of the pilot?
1. Understand how jurisdictions are using geocoding
2. Understand the data workflow, processes, and burden of jurisdictions reporting to a CDC program
3. Understand what else should be included in a Geocoding Building Block to make it useful for jurisdictions who might use it
## What is the level of commitment required?
- Pilot partners submit a “Become a Geocoding Pilot Partner” issue on Github. 
    - Pilot partner schedules a 15 minute call to share API authentication credentials for a subsidized Smarty license current geocoding workflow
- Pilot partners use Geocoding Building Block at least once 
    - Partner installs the SDK 
    - Partner uses the geospatial module to geocode healthcare data, for ongoing geocoding needs or for a single batch process. This can be locally on an individual device or integration in a cloud-hosted pipeline. 
- Pilot partners complete a follow up survey 
- Pilot partners participate in 30 minute follow-up call for deep-dive on topics surfaced in the survey related to usage of the geospatial module 
## How do I get involved?
- File a “Become a Geocoding Pilot Partner” ticket in the phdi repo.  
# Pilot Onboarding and Support
## Onboarding 

**Installing the SDK** 

- Follow the “[Getting Started](https://github.com/CDCgov/phdi#getting-started)”  instructions to install the SDK in an appropriate Python environment. 
- Read through the [Geospatial Tutorial](https://github.com/CDCgov/phdi#getting-started) for more detail about using the geospatial module. 

**Receiving a CDC subsidized Smarty license (API key)**

- Create a ticket in the `phdi` repo to request to become a Geocoding Pilot partner. Creating this ticket will kick-off the process to retrieve a CDC-subsidized Smarty license.  
- A PHDI team member will respond on the ticket to set up an unrecorded call to screenshare API authentication credentials for your STLT. 
- Record those credentials in a secure place!
- Use those credentials to authenticate in the phdi SDK.
## Technical Support

For technical support, please **create tickets in the phdi Github repo** using the Support issue template provided.

# Feedback 

**Survey** 
After using our geospatial module, we will send over a SurveyMonkey survey to gather feedback across the following topics.

- Data quality 
- Installation ease of use
- SDK ease of use 
- Support & Documentation
- Subsidized Smarty License

**Follow-up Call**
We’ll then schedule a 30 minute feedback call to dive deeper into topics highlighted in the survey.


