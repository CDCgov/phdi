## Getting Started with DIBBs HTML Insights

### Introduction
The PHDI HTML Insights app offers a REST API for processing FHIR messages into an HTML page with key insights.

### Running HTML Insights

The HTML Insights app can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Node.js source code.

#### Running with Docker (Recommended)

To run the HTML Insights app with Docker, follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/html-converter:latest`.
3. Run the service with `docker run -p 8080:8080 html-converter:latest`.

Congratulations, the HTML Insights app should now be running on `localhost:8080`!

#### Running from Node.js Source Code

We recommend running the HTML Insights app from a container, but if that is not feasible for a given use-case, it may also be run directly from Node using the steps below.

1. Ensure that both Git and Node 18.x or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/html-converter/`.
5. Install all of the Node dependencies for the HTML Insights app with `npm install`.
6. Run the HTML Insights app on `localhost:8080` with `npm start`. 

### Building the Docker Image

To build the Docker image for the HTML Insights app from source instead of downloading it from the PHDI repository follow these steps.
1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/html-converter/`.
4. Run `docker build -t html-converter .`.
