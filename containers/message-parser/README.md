## Getting Started with the DIBBs Message Parser

### Introduction

The DIBBs Message Parser offers a REST API for extracting desired fields from a given message. The service natively supports extracting values from FHIR bundles, but it can support parsing Hl7v2 (eLR, VXU, ADT, etc.) and CDA(eCR) messages by first using the [DIBBs FHIR Converter](https://cdcgov.github.io/phdi/latest/containers/fhir-converter.html) to convert them to FHIR. Fields are extracted using a "parsing schema" which is simply a mapping in key:value format between desired field names (keys) and the [FHIRPaths](https://build.fhir.org/fhirpath.html) within the bundle to the values. In addition the data type of value (string, integer, float, boolean, date, timestamp) as well as whether the value can be null (`true`, `false`) must be specified. A simple example of a schema for extracting a patient's first and last name from messages is shown below.

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

Sometimes healthcare messages can be large and complex. A single message might contain several lab results that all must be extracted. We could do this by mapping each lab to its own column, `"lab_result_1", "lab_result_2", "lab_result_3"` and so on. However, this is cumbersome if the possible number of labs is unknown or very large. To address this the Message Parser can return multiple values found in equivalent locations in a FHIR bundle as an array. To do this we can add the `"secondary_schema"` key to the field of a parsing schema that should contain multiple values. The example schema below demonstrates extracting a patient's first name, last name, as well as all of their labs.

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

You can run the Message Parser using Docker, any other OCI container runtime (e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the Message Parser with Docker, follow these steps.

1. Confirm that you have Docker installed by running `docker -v`. If you don't see a response similar to what's shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.

```
❯ docker -v
Docker version 20.10.21, build baeda1f
```

2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/message-parser:latest`.
3. Run the service with ` docker run -p 8080:8080 message-parser:latest`.

Congratulations, the Message Parser should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the Message Parser from a container, but if that isn’t feasible for a given use case, you can also run the service directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows Power Shell).
6. Install all of the Python dependencies for the Message Parser with `pip install -r requirements.txt` into your virtual environment.
7. Run the FHIR Converter on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`.

### Building the Docker Image

To build the Docker image for the Message Parser from source instead of downloading it from the PHDI repository follow these steps.

1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Run `docker build -t message-parser .`.

### The API

When viewing these docs from the `/redoc` endpoint on a running instance of the message parser or the DIBBs website, detailed documentation on the API will be available below.

### Architecture Diagram

````mermaid
flowchart LR

subgraph requests["Requests"]
    direction TB
    subgraph GET["fas:fa-download <code>GET</code>"]
        hc["<code>/</code>\n(Health Check)"]
        schemas["<code>/schemas</code>\n(Schema List)"]
        specificSchema["<code>/schemas/{parsing_schema_name}</code>\n(Specific Schema)"]
    end

    subgraph POST["fas:fa-upload <code>POST</code>"]
        parseMessage["<code>/parse_message</code>\n(Parse HL7v2, eICR, FHIR)"]
        fhirToPhdc["<code>/fhir_to_phdc</code>\n(FHIR To PHDC)"]
    end

    subgraph PUT["fas:fa-upload <code>PUT</code>"]
        uploadSchema["<code>/schemas/{parsing_schema_name}</code>\n(Upload Schema)"]
    end
end

subgraph service[REST API Service]
    direction TB
    subgraph container["fab:fa-docker container"]
    parser["fab:fa-python <code>message-parser<br>HTTP:8080/</code>"]
    end
end

subgraph response["Responses"]
    subgraph JSON["fa:fa-file-alt <code>JSON</code>"]
        rsp-hc["fa:fa-file-code <code>OK</code> fa:fa-thumbs-up"]
        rsp-schemas["fa:fa-file-code Schema List"]
        rsp-specificSchema["fa:fa-file-code Specific Schema"]
        rsp-parseMessage["fa:fa-file-code Parsed Message"]
        rsp-fhirToPhdc["fa:fa-file-code PHDC Document"]
        rsp-uploadSchema["fa:fa-file-code Schema Upload Status"]
    end
end

hc -.-> parser -.-> rsp-hc
schemas -.-> parser -.-> rsp-schemas
specificSchema -.-> parser -.-> rsp-specificSchema
parseMessage ==> parser ==> rsp-parseMessage
fhirToPhdc ==> parser ==> rsp-fhirToPhdc
uploadSchema --> parser --> rsp-uploadSchema```
````
