## The PHDI Tabulation Service

### Introduction
The PHDI Tabulation Service offers a containerized web services that exposes an HTTP endpoint for extracting, tabulating, and persisting data from a FHIR server according to a user-defined schema. This is done using functionality from the `tabulation` package in the `phdi` library available [here](https://github.com/CDCgov/phdi/tree/main/phdi/tabulation). Detailed documentation on the `/tabulate` endpoint is available [here](#the-convert-to-fhir-endpoint)

### Running the Tabulation Service

The Tabulation Service can be run using Docker (or any other OCI container runtime e.g. Podman), or directly from the Python sorce code.

#### Running with Docker (Recommended)

To run the Tabulation Service with Docker follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/phdi-tabulation:main`.
3. Run the service with `docker run -p 8080:8080 phdi-tabulation`.

Congradulations the Tabulation Service should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the Tabulation Service from a container, but if that is not feasible for a given use-case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/phdi-tabulation/`.
4. Install all of the dependencies with `pip install -r requirements.txt`. We recommend that you do this in Python virtual environment.
5. Run the Tabulation Service on `localhost:8080` with `uvicorn main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the Tabulation Service from source instead of downloading it from the PHDI repository follow these steps.
1. Ensure that bother Git and Docker are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/phdi-tabulation/`.
4. Run `docker build -t phdi-tabulation .`

### The /tabulate Endpoint 

Below you will find detailed documentation about the `/tabulate` endpoint and how to use it. 
