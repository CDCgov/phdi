ARG ALERTS_URL
ARG FHIR-CONNECTOR_URL
ARG INGESTION_URL
ARG MESSAGE-PARSER_URL

FROM python:3.10-slim

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY ./app /code/app
COPY ./assets /code/assets
COPY ./description.md /code/description.md

ENV ALERTS_URL=$ALERTS_URL
ENV FHIR-CONNECTOR_URL=$FHIR-CONNECTOR_URL
ENV INGESTION_URL=$INGESTION_URL
ENV MESSAGE-PARSER_URL=$MESSAGE-PARSER_URL

EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080