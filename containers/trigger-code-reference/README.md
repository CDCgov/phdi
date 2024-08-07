## Getting Started with the DIBBs Trigger Code Reference Service

### Introduction

The DIBBs Trigger Code Reference (TCR) service offers a REST API devoted to querying and enriching SNOMED condition code analysis. This service stores condition codes and their associated value sets, which users can query and insert into supplied FHIR bundles as tagged extensions for future path parsing.

### Running the Trigger Code Reference Service

You can run the TCR using Docker. another OCI container runtime (e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the trigger code reference with Docker, follow these steps.

1. Confirm that you have Docker installed by running docker -v. If you don't see a response similar to what's shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.

```
❯ docker -v
Docker version 20.10.21, build baeda1f
```

2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/trigger-code-reference:latest`.
3. Run the service with ` docker run -p 8080:8080 trigger-code-reference:latest`.

Congratulations, the TCR should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the TCR from a container, but if that isn't feasible for a given use case, you can also run the service directly from Python using the steps below.

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
4. Run `docker buildx build --platform linux/amd64 -t trigger-code-reference .`.

### The API

When viewing these docs from the `/redoc` endpoint on a running instance of the TCR or the DIBBs website, detailed documentation on the API will be available below.

### Architecture Diagram

```mermaid
flowchart LR

subgraph requests["Requests"]
    direction TB
    subgraph GET["fas:fa-download <code>GET</code>"]
        hc["<code>/</code>\n(Health Check)"]
        getValueSets["<code>/get-value-sets</code>\n(Get Value Sets for Condition)"]
    end
    subgraph POST["fas:fa-upload <code>POST</code>"]
        stampConditionExtensions["<code>/stamp-condition-extensions</code>\n(Stamp Condition Extensions)"]
    end
end

subgraph service[REST API Service]
    direction TB
    subgraph container["fab:fa-docker container"]
        tcr["fab:fa-python <code>trigger-code-reference<br>HTTP:8080/</code>"]
        db["fas:fa-database SQLite DB"]
    end
end

subgraph response["Responses"]
    subgraph JSON["fa:fa-file-alt <code>JSON</code>"]
        rsp-hc["fa:fa-file-code <code>OK</code> fa:fa-thumbs-up"]
        rsp-getValueSets["fa:fa-file-code Value Sets"]
        rsp-stampConditionExtensions["fa:fa-file-code Stamped Bundle"]
    end
end

hc -.-> tcr -.-> rsp-hc
getValueSets -.-> tcr -.-> rsp-getValueSets
stampConditionExtensions ==> tcr ==> rsp-stampConditionExtensions
tcr --> db
```
