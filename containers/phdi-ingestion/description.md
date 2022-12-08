## Getting Started with the PHDI Ingestion Service

### Introduction
The PHDI Ingestion Service offers a containerized web-API that provides HTTP endpoints for each of the Building Blocks that compose the Ingestion Pipeline, except FHIR conversion. A dedicated FHIR conversion service is available [here](https://github.com/CDCgov/phdi/tree/main/containers/fhir-converter).

### Available Functionality

The table below offers a brief summary the endpoints and their functionalty currently supported by the Ingestion Service. Detailed documentation about the API and all of the endpoints is available [here](#detailed-endpoint-documentation). Alternatively, you may also view this more documentation by spinning up your own instance of the service by following [these directions](#running-the-ingestion-service) and visit the `/docs` endpoint.

| Endpoint | Description |
| -------- | ----------- |
| Standardize Names | Standardize patient names in FHIR bundles and resources. |
| Standardize Phones | Standardize patient phone numbers in FHIR bundles and resources. |
| Geocode | Geocode patient addresses in FHIR bundles and resources using the Smarty or US Census geocoding services. |
| Add Patient Identifier | Add a hashed patient identifier to FHIR bundles that can be used for record linkage and patient de-duplication. |
| FHIR Bundle Upload | Upload a FHIR bundle to a FHIR server. |


### Running the Ingestion Service

The Ingestion Service can be run using Docker (or any other OCI container runtime e.g. Podman), or directly from the Python sorce code.

#### Running with Docker (Recommended)

To run the Ingestion Service with Docker follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/phdi-ingestion:main`.
3. Run the service with `docker run -p 8080:8080 phdi-ingestion`.

Congradulations the Ingestion Service should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the Ingestion Service from a container, but if that is not feasible for a given use case it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/phdi-ingestion/`.
4. Install all of the dependencies with `pip install -r requirements.txt`. We recommend that you do this in Python virtual environment.
5. Run the Ingestion Service on `localhost:8080` with `uvicorn app.main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the Ingestion Service from source instead of downloading it from the PHDI repository follow these steps.
1. Ensure that bother Git and Docker are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/phdi-ingestion/`.
4. Run `docker build -t phdi-ingestion .`

### Detailed Endpoint Documentation

Below you will find detailed documentation about each of the endpoints on the Ingestion Service.

#### A note on API design
Each endpoint on the Ingestion Service implements a Building Block imported from the PHDI python library [phdi](https://pypi.org/project/phdi/). For consistency between `phdi` and the API on this service, the path to each endpoint corresponds to the location in `phdi` of the Building Block  that it implements. For example, the `standardize_names` function for FHIR resources and bundles can be imported from `phdi` with `from phdi.fhir.harmonization.standardization import standardize_names` and the `standardiz_names` endpoint on this service is located at `/fhir/harmonization/standardization/standardize_names`. 
