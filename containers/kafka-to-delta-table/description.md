## Getting Started with the DIBBs Kafka to Delta Table Streaming Service

### Introduction
The Kafka to Delta table streaming service offers a REST API for streaming JSON formatted data from a [Kafka](https://kafka.apache.org/) topic to a [Delta table](https://delta.io/). The service currently supports reading from Kafka running on a local machine, and [Azure Event Hub](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about) via its [Kafka endpoint](https://learn.microsoft.com/en-us/azure/event-hubs/azure-event-hubs-kafka-overview). The service can write to a local files system, or to [Azure Data Lake Gen2](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction). In order to properly parse the data it receives from Kafka the service must be provided with its schema. In the example schema shown below the service will attempt to extract string values stored in the "first_name" and "last_name" keys of every JSON payload it reads from Kafka. It will then append these values to the "first_name" and "last_name" column of a Delta table as a new row. In the future support may be added for uploading schemas as .json files to the service so that they do not need need to be passed with every request. 


```
{
    "first_name":"string",
    "last_name":"string",
}
```

### Running the Kafka to Delta Table Streaming Service

The Kafka to Delta table streaming service can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

#### Running with Docker (Recommended)

To run the Kafka to Delta table streaming service with Docker, follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/message-parser:main`.
3. Run the service with ` docker run -p 8080:8080 message-parser:main`.

Congratulations, the Kafka to Delta table streaming service should now be running on `localhost:8080`!

#### Running from Python Source Code

We recommend running the Kafka to Delta table streaming service from a container, but if that is not feasible for a given use-case, it may also be run directly from Python using the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows Power Shell).
5. Install all of the Python dependencies for the Kafka to Delta table streaming service with `pip install -r requirements.txt` into your virtual environment.
6. Run the FHIR Converter on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the Kafka to Delta table streaming service from source instead of downloading it from the PHDI repository follow these steps.
1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/message-parser/`.
4. Run `docker build -t message-parser .`.

### The API 

When viewing these docs from the `/redoc` endpoint on a running instance of the Kafka to Delta table streaming service or the PHDI website, detailed documentation on the API will be available below. 