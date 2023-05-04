## Getting Started with the PHDI Ingestion Service

### Introduction
The PHDI ingestion service offers a REST API with endpoints for standardization and harmonization of FHIR messages. It offers name standardization, date of birth standardization, phone number standardization, geocoding, and several utilities for working with FHIR servers.

### Running the Ingestion Service

The ingestion service can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended for production)

To run the ingestion service with Docker follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/ingestion:main`.
3. Run the service with ` docker run -p 8080:8080 ghcr.io/cdcgov/phdi/ingestion:main`.

Congratulations, the ingestion service should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the ingestion service from a container, but if that is not feasible for a given use case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/ingestion/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows PowerShell).
5. Install all of the Python dependencies for the ingestion service with `pip install -r requirements.txt` into your virtual environment.
6. Run the FHIR Converter on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the ingestion service from source code instead of downloading it from the PHDI repository, follow these steps.
1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/ingestion/`.
4. Run `docker build -t ingestion .`.

### The API 

When viewing these docs from the `/redoc` endpoint on a running instance of the ingestion service or the PHDI website, detailed documentation on the API will be available below. 
