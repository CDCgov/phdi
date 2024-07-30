## Getting Started with the DIBBs Message Refiner Service

### Introduction

The DIBBs message refiner service offers a REST API to pare down an incoming message to only the user-specified elements.

### Running the eCR Refiner

The message refiner can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the message refiner with Docker, follow these steps.

1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.

```
❯ docker -v
Docker version 20.10.21, build baeda1f
```

2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/message-refiner:latest`.
3. Run the service with ` docker run -p 8080:8080 message-refiner:latest`.

Congratulations, the message refiner should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the message refiner from a container, but if that is not feasible for a given use-case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-refiner/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows Power Shell).
6. Install all of the Python dependencies for the message refiner with `pip install -r requirements.txt` into your virtual environment.
7. Run the message refiner on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`.

### Building the Docker Image

To build the Docker image for the message refiner from source instead of downloading it from the PHDI repository follow these steps.

1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-refiner/`.
4. Run `docker build -t message-refiner .`.

### The API

When viewing these docs from the `/redoc` endpoint on a running instance of the message refiner or the PHDI website, detailed documentation on the API will be available below.

### Architecture Diagram

<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.1/css/font-awesome.min.css">

```mermaid
flowchart LR

subgraph requests["Requests"]
direction TB
subgraph GET["fas:fa-download <code>GET</code>"]
hc["<code>/</code>\n(health check)"]
example["<code>/example-collection</code>\n(Example Requests)"]
end
subgraph PUT["fas:fa-upload <code>PUT</code>"]
ecr["<code>/ecr</code>\n(refine eICR)"]
end
end

subgraph service[REST API Service]
direction TB
subgraph mr["fab:fa-docker container"]
refiner["fab:fa-python <code>message-refiner<br>HTTP:8080/</code>"]
end
subgraph tcr["fab:fa-docker container"]
tcr-service["fab:fa-python <code>trigger-code-reference<br>HTTP:8081/</code>"] <==> db["fas:fa-database SQLite DB"]
end
mr <==> |<code>/get-value-sets</code>| tcr
end

subgraph response["Responses"]
subgraph JSON["fa:fa-file-alt <code>JSON</code>"]
rsp-hc["fa:fa-file-code <code>OK</code> fa:fa-thumbs-up"]
rsp-example["fa:fa-file-code Postman Collection"]
end
subgraph XML["fas:fa-chevron-left fas:fa-chevron-right <code>XML</code>"]
rsp-ecr["fas:fa-file-code Refined eICR"]
end
end

hc -.-> mr -.-> rsp-hc
example --> mr --> rsp-example
ecr ===> mr ===> rsp-ecr

```

### Additional notes on eICR Refinement

For further details on `<section>`, `<entry>`, and `<templateId>` elements, please see [eICR-Notes.md](eICR-Notes.md) for an explanation of trigger code `<templateId>`s, which sections they're in, and the `<observation>` data that should be returned in the refined eICR output.

```

```
