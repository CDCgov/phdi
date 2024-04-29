# Monitoring Systems Overview

This document outlines the components, concepts, and scope of the alerting and monitoring technologies used to track the DIBBs Orchestration Service. While it's not intended to be comprehensive, it should provide a high-level contextual overview of how and why various monitoring pieces are working together.

## Contents
* [Packages](#packages)
* [What Are The Pieces](#what-are-the-pieces-concepts-components-and-terms)
* [Types of Telemetry](#types-of-telemetry)
* [OpenTelemetry Basics and Configuration](#opentelemetry-basics-and-configuration)
* [The OTel Collector](#the-otel-collector)
* [The OTel Collector and Jaeger](#the-otel-collector-and-jaeger)
* [The OTel Collector and Prometheus](#the-otel-collector-and-prometheus)
* [How We've Set Things Up](#how-weve-set-things-up)
* [The Monitoring Flow](#the-monitoring-flow-this-creates)
* [Where This Happens In The Code](#where-this-happens-in-the-code)
* [Manual Tracing Instrumentation: Notes and Practices](#manual-tracing-instrumentation-notes-and-practices)


## Packages

* [**OpenTelemetry**](https://opentelemetry.io/docs/languages/python/): OpenTelemetry is one of the most prominent open-source monitoring and logging packages used today. It provides all the infrastructure needed to instrument, collect, and export telemetry data (which consists of traces, metrics, spans, and logs) to other services using the OpenTelemetry Protocol (or OTLP). It offers a staggering range of configuration options, which all need to be fine-tuned together to make telemetry systems work.
* [**Jaeger**](https://www.jaegertracing.io/docs/1.56/apis/): Jaeger (also known as Jaeger-All-in-One or JaegerTracing) is a backend observability tool used to analyze trace data. Jaeger tracks and monitors the span contexts of function calls in an application as requests cross service boundaries (e.g. when a request hits the Validation Service, then the FHIR Converter), then aggregates these spans to provide an accurate mapping of what happened in the application as the request propogated. It natively supports Open Telemetry's OTLP logging format, allowing it to integrate seamlessly with other OTLP tools in the OpenTelemetry ecosystem.
* [**Prometheus**](https://prometheus.io/docs/prometheus/latest/getting_started/): Prometheus is an extremely popular tool for application logging and monitoring. Prometheus specifically excels in time-series data point metrics aggregations, typically about system-wide performance or application health  (e.g. CPU usage, number of requests broken up by status code, etc.). Prometheus is what's called a "pull-based" retrieval system, meaning that it should be configured to scrape other API endpoints to fetch metrics data from them, rather than having data sent directly to it. It stores any metrics data it scrapes in a locally mounted storage volume.
* [**Grafana**](https://grafana.com/docs/grafana/latest/): The third element of the OTel / Prometheus ecosystem, Grafana is a visualization system that can display telemetry data in a variety of charts and dashboards. It is the most popular choice to back-end Prometheus, since a Prometheus storage volume can be specified as a Grafana-native data source and metrics loaded directly using the Prometheus Query  Language (PromQL).

## What Are The Pieces: Concepts, Components, and Terms

### Types of Telemetry

* _Traces_: Traces are "residues" or "footprints" that an API request leaves when it enters a system. When the request accesses its entrypoint, or is passed or sent to another service, it leaves a digital record of its processing time at each service along the way. Traces are used to track the information flow of a request in a distributed system, particularly as a request crosses "microservice boundaries" (i.e. when a request moves from processing in one service to another via HTTP request).
* _Spans_: Spans are sub-components of traces that capture the attributes, or "state", of an incoming request at a particular moment in time. If traces give the bird's eye view of a request moving through the system, spans provide the event-to-event details of how the information in that request changes as it's processed by each service in the system. OpenTelemetry spans are particularly powerful tools because the OTLP format essentially renders them as JSON-structured log outputs. This allows traces and spans to serve as a powerful debugging tool that captures event-driven information, as well as key-value attribute pairs, for any context or value propagating through the application.
* _Metrics_: Metrics are aggregations of counts over time (note: _all_ OpenTelemetry metrics are time-series by construction). While Traces track incoming or transported requests, Metrics measure system or request characteristics like latency, CPU load, time-to-request-completion, number of requests received, etc.
* _Logs_: Logs are the most self-explanatory kind of telemetry data, the usual fare of print and debug statements a service emits to record that an event has happened. Logs are traditionally used to denote event-based links in a system's processing, such as one function in a service concluding processing and another function in that same service starting up. Logs and Spans supplement one another with different views of the state of a request as it gets processed.

### OpenTelemetry Basics and Configuration

* _Instrumentation_: Instrumentation refers to the process of setting up a service to emit telemetry data (note that instrumentation refers only to _producing_ telemetry data, not doing anything with it). Instrumentation can be either manual or automatic (there's also a third option, programmatic, but for our purposes we won't be using that at all), or some combination of both.
* _Automatic Instrumentation_: This type of instrumentation allows a bootstrapped distribution of OpenTelemetry to scan a service's codebase and, on the back end, add in all the infrastructure context for producing telemetry data. Telemetry producers and consumers are created, combined, and wired together with a global context to make each API endpoint of a service emit a suite of standard information (including traces for all incoming requests, spans for request attributes, and metrics for application health and system performance).
* _Manual Instrumentation_: This type of instrumentation must be configured and implemented by a developer. In any case where you'd like to collect and emit information that isn't automatically collected--or you'd like to customize how a particular type of information is emitted--manual instrumentation is required. To instrument a piece of an application, you need three things: a Provider, an Agent, and an Instrument. These things aren't hard to set up, but do require invoking in the correct order.
* _Instrumentation Provider_: A global, module- or application-level information context that ensures telemetry is produced in the same place for the same file. A Provider also serves as the API gateway for developers to access OpenTelemetry functions. **For DIBBs, Automatic Instrumentation has already configured all module providers for us.**
* _Instrumentation Agent_: A module-level context responsible for managing everything that one part of the service will emit. Agents create and manage the individual instruments that collect information.
* _Instrumentation Instrument_: An instrument is a single piece of reportability code that tracks and emits data on one thing. A metric that counts the number of requests to a single endpoint is an instrument, for example.

### The OTel Collector

The OpenTelemetry Collector is a series of components that sits between the instrumented service and the storage/query/visualization backend (in our case, Prometheus, since Grafana networks with Prometheus rather than Orchestration directly). It's actually a pipeline through which telemetry data passes, and it's made up of three components:

* _Receiver_: A Collector's Receiver is the component responsible for gathering telemetry data produced by other parts of the system. A Receiver "listens" on a certain port for packeted telemetry sent to it by the Instrumentation Context, and when it detects telemetry packets on that port, it decodes them into an internal representation called OTLP (which is a specified machine protocol that telemetry data must comply with).
* _Processor_: A Collector's Processor is the component responsible for applying batch processing or filtering to the received data. For our purposes, we don't execute any steps here, so Processor is a no-op.
* _Exporter_ The Exporter is the component that actually sends OTLP-formatted data to the back-end. It is the most important part of the Collector since that's how telemetry actually reaches its end state. This data transmission is usually done on one of several ports available on the Collector, depending on the transport structure of the data (e.g. there's a port for gRPC format and a port for HTTP format). For DIBBs, the Exporter also has a secondary function: in addition to actually transmitting data to some parts of the backend (like Jaeger), the OTel Collector also _exposes_ the numerical information it's processed on a `/metrics` endpoint of its own hosted namespace. This allows a service like Prometheus to scrape that information at its own specified interval.

#### The OTel Collector and Jaeger

Jaeger is an excellent example of the Collector just _working_. As of 2022, all of Jaeger's basic data formats were switched to the OpenTelemetry OTLP standard. This means that all of its information is natively formatted the same as the information that comes out of the OTel Collector. Getting these two tools to talk to one another is as simple as pointing the correct port on the Collector to the equivalent port in the Jaeger container's namespace.

#### The OTel Collector and Prometheus

Prometheus, on the other hand, doesn't play quite so nicely. Confusingly, OpenTelemetry allows Prometheus to slot in as either a Receiver _or_ an Exporter in a Collector pipeline. Furthermore, if exporting with Prometheus, OpenTelemetry can be ambiguous about whether Prometheus is a destination that's going to receive data, _or_ if Prometheus is the entity that's going to _collect data from the Collector_ (yes, that is the actual terminology). To break this down, there are three possible cases worth enumerating (so that we can sanity check that future work is still following the pattern we want):

- Prometheus as Receiver: in this case, Prometheus is looking for telemetry data that's been instrumented in a system to be sent directly to Prometheus. The role of the Collector in this configuration is that OpenTelemetry is then going to collect metrics _about what Prometheus collected_, which is **not** what we want.
- Prometheus as entity being exported to: there's a configuration option allowable in both OpenTelemetry and Prometheus called `PrometheusRemoteWrite` that allows OpenTelemetry to send metrics directly to Prometheus' local backend storage via data push. While this technically gets data into Prometheus, it is **not** the system we want to use. Prometheus is optimized for pull-based data retrieval, so having OpenTelemetry use a push operation to just write directly to storage will disable some important time-series aggregation functionality that Prometheus provides.
- Prometheus as entity collecting from the OTel Collector: **this is the option we want to be using**. After shipping off formatted telemetry data to the console, the OTel Collector will make available all the metrics it processed at an endpoint local to its own service host. Exposing the metrics at this endpoint will allow the Prometheus periodic job configuration to query them at its own defined interval while still optimizing for pull-based efficiency.

## How We've Set Things Up

* We start by using OpenTelemetry's automatic instrumentation to create all of the Provider-level instrumentation contexts for the Orchestration Service. This is executed in the project's `Dockerfile`.
* We supplement the automatic instrumentation with manual instrumentation for both metrics and traces/spans for the `process-message` endpoint. This is instrumented in `main.py`.
* We spin up local instances of the OTel Collector, Jaeger, Prometheus, and Grafana, making sure to expose specific relative ports and endpoints. This is executed in the project's `docker-compose.yml`.
* We configure the OTel Collector with the listening/transmitting mechanisms we want to use, and then activate the Collector with a service pipeline. This is set up in `otel-collector-config.yaml`.
* We configure the Jaeger UI with a few visual options to customize how we want our menus laid out when data reaches the backend. This is set up in `jaeger-ui.json`.
* We configure Prometheus with a scrape job to fetch the metrics that the OTel Collector put together for us based on our instrumentation. This is configured in `prometheus.yml`.
* We link Prometheus to Grafana as its database source so that it can pull metrics from Prometheus' local DB into visualization dashboards.
* We configure `grafana/datasources/datasources.yml` to specify Prometheus connection as the default data source to use for the visualization in Grafana.
* We configure `grafana/dashboards/dashboard.yml` for the Dashboards we use throughout Grafana. New dashboards can be created in Grafana UI then downloaded as JSON and saved within the `grafana/dashboards` folder for use by any user logging into `localhost:4000`.

## The Monitoring Flow This Creates

When an API request hits the `process-message` endpoint of the Orchestration Service, it goes through the following process:

* The Instrumentation Provider for the Orchestration Service is activated (since Providers are module-level, and endpoints are all in the `main.py` folder, there is one Metrics Provider for the whole service), letting all the telemetry producers that are automatically or manually instrumented know that they have a job to do.
* The HTTP Request leaves a trace in the `process-message` endpoint, which is stored for the moment.
* The Request gets bounced around the various DIBBs services, emitting a trace for each service it passes through. These traces are used to calculate standard, automatically provided backend metrics like latency, time to completion, etc.
* Each of these traces also produces one or more spans containing key-value pairs that hold stateful information about the request, such as the API endpoint the request hit, the transmission method, the parameters in the request, or any other context added by the orchestration service and its instrumentation.
* The `process-message` function has finished calling all other DIBBs service and is about to return. When the Return value is created, before it's actually handed to the caller, a final trace is emitted. This trace is used in conjunction with the initial trace the request first created to calculate the time to completion of this request.
* Additionally, the status code that the `building_blocks_response` returned is copied by the Meter created at the top of the file. This Meter hands the status code to the metric responsible for counting calls to the `process-message` endpoint, which then uses a dictionary index to increment the number of calls that returned the particular status code by 1.
* The request is finished, computation has generated a Return value, and this is sent back to the user.
* After the return value is dispatched (we don't want the caller waiting on metrics calculation to get their answer), the Meter Provider sends all metrics generated or affected by this particular request to the OTLP export endpoint specified in our environment variables--in this case, `otel-collector:4318`.
* At the same time the Meter Provider dispatches metrics, the Tracer Provider collects all emitted spans and traces, bundles them into the OTLP format, and sends them to the trace endpoint specified in our environment variables--`otel-collector:4317`.
* The Collector's OTLP Receiver detects new information sent to one of its ports, so it retrieves that information and encodes it into OTLP standard.
* The Collector's Processor has no defined filtering or functionality, so it batches all this data together and passes it on.
* The Collector's Exporter first dumps a decoded copy of the telemetry data (from OTLP to human-readable) to the console for debugging.
* The Collector's `4317` port is connected directly to the `4317` port on the Jaeger backend (since the two packages share the same data format), so the trace and span data dumped there after encoding is processed straight into Jaeger's query store.
* At this point, trace data is available for direct searching and analysis at `localhost:16686`.
* Then, the Collector sends the original, still-encoded data to an endpoint at one of its own ports, namely `otel-collector:8889/metrics`.
* Any and all data that's been sent to `/metrics` without the `/metrics` endpoint being hit continues to remain there until the Prometheus `scrape_interval` hits.
* The local Prometheus server makes an API call to the Collector's `8889/metrics` endpoint, scraping the still-OTLP encoded data into its own local, in-container database.
* Prometheus data volumes are OTLP compatible, so the data doesn't need to be further encoded or modified before it's finally transferred to its end-destination mounted storage volume.
* Grafana then is configured via the `datasources.yml` file to use Prometheus as the data source.
* Grafana's UI can be accessed by navigating to `localhost:4000` (the endpoint specified in `docker-compose.yml` and `grafana.ini`) to create and view dashboards.
* In addition to dashboards, Grafana offers an Explore mode to query any data exposed by Prometheus to directly investigate metrics or issues.

## Where This Happens In The Code

### `Dockerfile`

We `pip install` and then execute a bootstrap command for an OpenTelemetry distro package. We also define some environment variables that are needed for the OTel collector to function properly:

- Each `OTEL_[TRACES/METRICS/LOGS]_EXPORTER` variable tells the Instrumentation Context what pathway to use for that typye of telemetry data. `None` means we don't want to see that data type at all, `Console` means print it to `STDOUT`, and `otlp` means use the OTLP protocol defined with the OTel Collector.
- Each `OTEL_EXPORTER_OTLP_[TRACES/METRICS/LOGS]_PROTOCOL` variable tells the Instrumentation Context how to send telemetry data so that the OTel Collector can understand it. By default, OpenTelemetry wires things over `gRPC`, but Python developer SDK notes strongly encourage `http/protobuf` wherever possible. Since Jaeger is based on native OTLP, it uses the gRPC format (over port `4317`), but for Prometheus (which ingests and decodes OTLP), we're able to use HTTP (over port `4318`).
- Each `OTEL_EXPORTER_OTLP_[TRACES/METRICS/LOGS]_ENDPOINT` tells the Instrumentation Context where to send telemetry so that the Collector can pick it up. The default port for `http/protobuf` is `4318`, and the default port for `gRPC` is `4317`, but note that the host is the `otel-collector` rather than the localhost container in which the entire service is running. Also, when multiple backend platforms get connected to the OTel Collector, the Collector uses appended endpoints to these ports to make sure data flows to the right place. So metrics data is available at endpoint `/v1/metrics` of the specified port, and trace data is available at `/v1/traces`.

### `main.py`

The top of the code shows a bit of manual instrumentation to create metrics for each endpoint that might be hit with a message processing request. Note that we don't need to create a Provider, since auto instrumentation does that for us, but we do still need to create a Meter (which is an Agent in the pattern) and then a Metric (which is an instrument).

### `docker-compose.yml`

The project's docker compose file is the heart of the connections needed to successfully emit, collect, and report telemetry data. In addition to spinning up the DIBBs services that Orchestration relies on, we also instantiate four other services needed for telemetry reporting:

- The OTel Collector: The Collector is its own service (since it is essentially a small data pipeline) and must be configured as such. Some things worth noting:
  * We use the `-contrib` image of the Collector because it offers a wider suite of parameterization and tuning options; the ordinary `opentelemetry-collector` image is extremely limited and not recommended for cloud use.
  * The `container_name` parameter is **critical**: since the Collector will be its own service, it _will not_ exist in the local namespace of the Orchestration Container or of Prometheus. Using the `container_name` parameter will allow us to specify the ports _hosted by the Collector_ as the ones we should be scraping for data (Docker will resolve this name for us into the Container's individual IP).
  * We need to mount the `otel-collector-config.yaml` file in the project directory into the appropriate directory in the Collector container, and then execute a config command once there.
  * We need to expose port 4317 (for g `RPC` export protocol, even though we don't send via it), port 4318 (the default `http/protobuf` destination), port 8888 (for metrics available about the collector's performance), and port 8889 (where we'll expose the actual metrics that come from the Orchestration service; this is the port Prometheus will scrape).
- Jaeger: Nothing too special here, just using the latest image of jaeger in conjunction with another mounted volume configuration like we did with the collector. 
- Prometheus: Same as with Jaeger above. The only thing of note is that if we want metrics storage to persist between container runs, we need to mount the storagae volume by defining `prom_data` explicitly.
- Grafana: Again, nothing out of the ordinary, just using some environment variables to securely authenticate.

### `otel-collector-config.yaml`

This file defines the configuration parameters for the OTel Collector we'll instantiate. The `http` and `grpc` port endpoints are the default values recommended with OpenTelemetry, but note that we preface the host as `0.0.0.0` because this configuration file is from the point of view of the Collector--these ports are local to it, so it can use its own hosted namespace rather than needing `otel-collector` like external services will. We want only the ordinary `otlp` receiver collecting information, have no particular filtering or processing operations, and want to send exported data to both the console (which is what `debug` means) and relevant backend services (Jaeger and Prometheus). Getting telemetry data to Jaeger is trivial; all we have to do is line up the `otlp` exporter endpoint destination with Jaeger's matching format port (`4317` for `gRPC`). Since the data is the same format for both, information flows directly into queryable storage with no other commands or operations on our part. To get it into Prometheus, we _don't_ push it via `remotewrite`, but instead expose an endpoint local to the Collector that Prometheus will periodically scrape. The `service` section of the config file actually activates all the components we defined, and specifies how each type of telemetry will be processed.

### `jaeger-ui.json`

A simple graphics specification file that tells Jaeger how we want our menu options to look when we open the Jaeger monitoring dashboard at `localhost:16686`. Our configuration options let the UI know which menu options we want visible, how far back to display trace query results, and have a pair of external-facing routes to connect to our other monitoring tools for easy switching.

### `prometheus.yml`

A simple specification that tells Prometheus how to collect the metrics data. All prometheus config files must start with the `global` and `scrape_interval` header, and then feature a `scrape_config` section that defines the jobs Prometheus will perform. The Orchestration Monitor has a single job, which is to aggregate telemetry metrics from the OTel Collector, so we provide port 8889 on host `otel-collector` as the target to get those metrics.

### `grafana.ini`

The primary configuration file for Grafana specifices various settings to customize and secure Grafana. 

* `paths` defines the directory paths for Grafana components, such as where it stores data, logs, plugins, and provisioning.
* `server` defines settings related to the Grafana webserver, including the port, domain name, and public URL.
* `database` is the configuration for Grafana's own database, which is separate from Prometheus' database.
* `log` controls the logging mechanism. Right now, logs are output to console and at the info level.
* `security` settings is where the admin_user and admin_password can be specified.
* `users` are user-specific settings. Right now, we allow users to sign-in and create accounts, but we may want to revisit if we want to create a user hierarchy (admin, read-only user, etc.).

### `grafana/dashboards/dashboard.yml`

This is a simple yaml file that specifies that dashboards saved here should be pulled in and loaded to the Grafana UI. New dashboards can be created in the UI then downloaded and saved here as JSON.

### `grafana/datasource/datasource.yml`

This is a simple yaml file that specifies the default data source for Grafana, which for our purposes is `prometheus:9090`.

## Manual Tracing Instrumentation: Notes and Practices

Automatic tracing instrumentation provides an out-of-the-box, halfway there solution to capturing what happens inside the Orchestration Service. However, the spans it produces as part of tracing a request capture information only at the edges of a system--incoming/outgoing HTTP requests, service boundary changes, etc. These spans don't provide any insight into what's happening inside a particular part of the service, nor do they sufficiently capture stateful attributes or logging events. To improve visibility for both logging and debugging, the Orchestration Service augments the bootstrapped automatic distribution with manual tracing instrumentation. Manual tracers relate to automatic tracers in the same way that manual metrics relate to automatic metrics: an instrumentation provider exists globally to oversee the application's lifecycle, and this provider generates agents that monitor various parts of the system.

In practice, we want to balance between richenss of logging information, granularity of control, and the risk of debugging clutter, all while avoiding duplication of tracing already provided by the automatic agent. OpenTelemetry suggests the following best practices when supplementing trace data:

* Let the automatic instrumentation manage the global tracer context and tracer requests, and instead focus manual instrumentation on creating and enriching spans. OpenTelemetry will automatically aggregate and order these spans into a coherent trace when the telemetry data is exported.
* Spans represent a single unit or "chunk" of work within the system, which means their most common scope should be a block of code with a defined start and end time. This almost always means spans should be scoped to functions (i.e. a one function, one span pattern).
* Use key-value attribute pairs within spans to record properties, request context, user information, or other metadata for which the timestamp of that metada isn't important. When setting attributes, prefer initializing them at span creation so that they can be fetched by OpenTelemetry's sampling processor (a subprocess used in several back-end SDK functions and OTel API calls).
* Use span events (rather than attributes) to record single moments in time at which a "significant" task is completed inside of a span's function--for example, recording a primitive log statement and timestamp to mark when a webpage becomes interactive.