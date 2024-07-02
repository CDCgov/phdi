ARG INGESTION_URL
ARG MESSAGE-PARSER_URL
ARG TRIGGER_CODE_REFERENCE_URL
ARG SMARTY_AUTH_ID
ARG SMARTY_AUTH_TOKEN

FROM ghcr.io/cdcgov/phdi/dibbs

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
RUN opentelemetry-bootstrap -a install

COPY ./app /code/app
COPY ./assets /code/assets
COPY ./description.md /code/description.md

ENV INGESTION_URL=$INGESTION_URL
ENV MESSAGE-PARSER_URL=$MESSAGE-PARSER_URL
ENV TRIGGER_CODE_REFERENCE_URL=$TRIGGER_CODE_REFERENCE_URL
ENV SMARTY_AUTH_ID=$SMARTY_AUTH_ID
ENV SMARTY_AUTH_TOKEN=$SMARTY_AUTH_TOKEN
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=none

# Prometheus preferred transfer is via HTTP
ENV OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://otel-collector:4318/v1/metrics

# Jaeger preferred routing is gRPC for native OTLP
ENV OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=grpc
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://otel-collector:4317/v1/traces

# Install curl for health check
RUN apt-get update && apt-get install -y curl

EXPOSE 8080
RUN export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
CMD opentelemetry-instrument --service_name dibbs-orchestration uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log_config.yml