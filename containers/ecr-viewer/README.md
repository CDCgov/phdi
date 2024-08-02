## Getting Started with DIBBs eCR Viewer

### Introduction

The DIBBs eCR Viewer service offers a REST API for processing eCR FHIR messages into an HTML page that displays key information in a readable format and makes specific data fields easy to find.

### Running eCR Viewer

You can run the eCR Viewer using Docker,  any other OCI container runtime (e.g., Podman), or directly from the Node.js source code. 

#### Running with Docker (Recommended)

To run the eCR Viewer with Docker, follow these steps.

1. Confirm that you have Docker installed by running `docker -v`. If you don't see a response similar to what's shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.

```
❯ docker -v
Docker version 20.10.21, build baeda1f
```

2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/ecr-viewer:latest`.
3. Run the service with `docker run -p 8080:8080 ecr-viewer:latest`.

Congratulations, the eCR Viewer should now be running on `localhost:8080`!

#### Running from Node.js Source Code

We recommend running the eCR Viewer from a container, but if that isn't feasible for a given use-case, it may also be run directly from Node using the steps below.

1. Ensure that both Git and Node 18.x or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/ecr-viewer/`.
4. Install all of the Node dependencies for the eCR Viewer with `npm install`.
5. Run the eCR Viewer on `localhost:3000` with `npm run dev`.

### Building the Docker Image

To build the Docker image for the eCR Viewer from source instead of downloading it from the PHDI repository follow these steps.

1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/ecr-viewer/`.
4. Run `docker build -t ecr-viewer .`.

### Running via docker-compose

The eCR Viewer requires a Postgres database with FHIR bundles to render properly. To make local development easier, a docker-compose file has been created that starts a Postgres database, seeds it with eCR FHIR data, and starts the Node service. This can be run with `docker compose up`. See the [Docker Compose documentation](https://docs.docker.com/engine/reference/commandline/compose_up/) for additional information.

### Non Integrated Viewer 

To enable the Non Integrated Viewer homepage, set the environment variable `NEXT_PUBLIC_NON_INTEGRATED_VIEWER` equal to `true`. This will enable the Non Integrated viewer homepage at `localhost:3000`.

For local development, if `NEXT_PUBLIC_NON_INTEGRATED_VIEWER` is not set equal to `true` on `.env.local`, convert-seed-data will not seed the metadata.

### Updating Seed Data

Occasionally, the FHIR Converter will be updated, which requires regenerating new seed data. You can do this  by running `npm run convert-seed-data`. To load the new data, you will have to delete the current volume used by your DB. 

### Potential Issues

If you have problems connecting your database run this command to see what other postgres databases are running
`sudo lsof -i :5432`

then kill it
`kill {pid}`

### Developer Documentation
Can be found in [api-documentation.md](api-documentation.md).