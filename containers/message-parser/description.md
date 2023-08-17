## Getting Started with the DIBBs Message Parser

### Introduction
The PHDI message parser offers a REST API for extracting desired fields from a given message. The service natively supports extracting values from FHIR bundles, but it can support parsing Hl7v2 (eLR, VXU, ADT, etc.) and CDA(eCR) messages by first using the [DIBBs FHIR converter](https://cdcgov.github.io/phdi/latest/containers/fhir-converter.html) to convert them to FHIR. Fields are extracted using a "parsing schema" which is simply a mapping in key:value format between desired field names (keys) and the [FHIRPaths](https://build.fhir.org/fhirpath.html) within the bundle to the values. In addition the data type of value (string, integer, float, boolean, date, timestamp) as well as whether the value can be null (`true`, `false`) must be specified. A simple example of a schema for extracting a patient's first and last name from messages is shown below.

```
{
  "first_name": {
    "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().given.first()",
    "data_type": "string",
    "nullable": true
  },
  "last_name": {
    "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().family",
    "data_type": "string",
    "nullable": true
  }
}
```

Using this schema on a message about a patient named John Doe yield a result like this.

```
{
  "first_name": "John",
  "last_name": "Doe"
}
```
### Nested Data

Sometimes healthcare messages can be large and complex. A single message might contain several lab results that all must be extracted. We could do this by mapping each lab to its own column, `"lab_result_1", "lab_result_2", "lab_result_3"` and so on. However, this is cumbersome and often a poor solution if the possible number of labs is unknown or very large. To address this the message parser can return multiple values found in equivalent locations in a FHIR bundle as an array. To do this we can add the `"secondary_schema"` key to the field of a parsing schema that should contain multiple values. The schema below demonstrates extracting a patient's first name, last name, as well as all of their labs.

```
{
  "first_name": {
    "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().given.first()",
    "data_type": "string",
    "nullable": true
  },
  "last_name": {
    "fhir_path": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().family",
    "data_type": "string",
    "nullable": true
  },
  "labs": {
        "fhir_path": "Bundle.entry.resource.where(resourceType='Observation').where(category.coding.code='laboratory')",
        "data_type": "array",
        "nullable": true,
        "secondary_schema": {
          "test_type": {
              "fhir_path": "Observation.code.coding.display",
              "data_type": "string",
              "nullable": true
          },
          "test_type_code": {
              "fhir_path": "Observation.code.coding.code",
              "data_type": "string",
              "nullable": true
          },
          "test_result": {
              "fhir_path": "Observation.valueString",
              "data_type": "string",
              "nullable": true
          },
          "specimen_collection_date": {
              "fhir_path": "Observation.extension.where(url='http://hl7.org/fhir/R4/specimen.html').extension.where(url='specimen collection time').valueDateTime",
              "data_type": "datetime",
              "nullable": true
          }
        }
    }
}
```

If this parsing schema is used on a message about a patient named Jane Doe with two labs the service would a return a result like this.

```
{
  "first_name": "Jane",
  "last_name": "Doe",
  "labs": [
    {
      "test_type": "Campylobacter, NAAT",
      "test_type_code": "82196-7",
      "test_result": "Not Detected",
      "specimen_collection_date": "2023-01-31T18:52:00Z"
    },
    {
      "test_type": "C. Diff Toxin A/B, NAAT",
      "test_type_code": "82197-5",
      "test_result": "Not Detected",
      "specimen_collection_date": "2023-01-31T18:52:00Z"
    }
  ]
}
```

### Running the Message Parser

The message parser can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the message parser with Docker, follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/message-parser:latest`.
3. Run the service with ` docker run -p 8080:8080 message-parser:latest`.

Congratulations, the message parser should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the message parser from a container, but if that is not feasible for a given use-case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows Power Shell).
5. Install all of the Python dependencies for the message parser with `pip install -r requirements.txt` into your virtual environment.
6. Run the FHIR Converter on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the message parser from source instead of downloading it from the PHDI repository follow these steps.
1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Run `docker build -t message-parser .`.

### The API 

When viewing these docs from the `/redoc` endpoint on a running instance of the message parser or the PHDI website, detailed documentation on the API will be available below. 
