## Getting Started with the DIBBs Message Parser

### Introduction
The PHDI message parser offers a REST API for extracting desired fields from a given message. The service natively supports extracting values from the FHIR bundles, but it can support parsing Hl7v2 (eLR, VXU, ADT, etc.) and CDA(eCR) messages by first using the DIBBs FHIR converter to convert them to FHIR. Fields are extracted using a "parsing schema" which is simply a mapping in key:value format between desired field names (keys) and the FHIR paths inside a FHIR bundle where the values can be found. A simple example of a schema for extracting a patient's first and last name from messages is shown below.


```
{
    "first_name":"Bundle.entry.resource.where(resourceType = 'Patient').name.first().given.first()",
    "last_name":"Bundle.entry.resource.where(resourceType = 'Patient').name.first().family",
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
