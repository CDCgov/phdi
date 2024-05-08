## bGetting Started with the DIBBs Trigger Code Reference  Service

### Introduction

The DIBBs Trigger Code Reference (trigger-code-reference) service offers a REST API devoted to querying and enriching SNOMED condition code analysis. This service stores condition codes and their associated value sets so that they can be queried by users, as well as inserted into supplied FHIR bundles as tagged extensions for future path parsing.

### Running the Trigger Code Reference Service

The trigger code reference can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the trigger code reference with Docker, follow these steps.

1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.

```
❯ docker -v
Docker version 20.10.21, build baeda1f
```

2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/trigger-code-reference:latest`.
3. Run the service with ` docker run -p 8080:8080 trigger-code-reference:latest`.

Congratulations, the trigger code reference should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the trigger code reference from a container, but if that is not feasible for a given use-case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/trigger-code-reference/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows Power Shell).
6. Install all of the Python dependencies for the tr with `pip install -r requirements.txt` into your virtual environment.
7. Run the trigger code reference on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`.

### Building the Docker Image

To build the Docker image for the trigger code reference from source instead of downloading it from the PHDI repository follow these steps.

1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/trigger-code-reference/`.
4. Run `docker build -t trigger-code-reference .`.

### The API

When viewing these docs from the `/redoc` endpoint on a running instance of the trigger-code-reference or the PHDI website, detailed documentation on the API will be available below.
