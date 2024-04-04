ARG INGESTION_URL
ARG MESSAGE-PARSER_URL
ARG SMARTY_AUTH_ID
ARG SMARTY_AUTH_TOKEN

FROM python:3.11.5-slim

WORKDIR /code

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git build-essential

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
RUN opentelemetry-bootstrap -a install

COPY ./app /code/app
COPY ./assets /code/assets
COPY ./description.md /code/description.md

ENV INGESTION_URL=$INGESTION_URL
ENV MESSAGE-PARSER_URL=$MESSAGE-PARSER_URL
ENV SMARTY_AUTH_ID=$SMARTY_AUTH_ID
ENV SMARTY_AUTH_TOKEN=$SMARTY_AUTH_TOKEN
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=none
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318


EXPOSE 8080
RUN export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
CMD opentelemetry-instrument --service_name dibbs-orchestration uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log_config.yml