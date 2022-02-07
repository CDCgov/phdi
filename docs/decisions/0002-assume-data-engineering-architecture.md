# 2. Assume the Architecture of Data Engineering With Apache Spark, Delta Lake, and Lakehouse

Date: 2022-02-07

## Status

Proposed

## Context and Problem Statement

Our team has had several conversations recently that relate to our planned architecture and infrastructure for the prototype period of this project. This proposal covers how to create and evolve our project's architecture over time.

## Decision Drivers

1. **Duration** - We only have a limited amount of time for our prototype
2. **Coherence** - We want to adopt a framework that covers an end-to-end solution for processing data
3. **Precedent** - We want to avoid reinventing the wheel where we don't have to
4. **Simplicity** - We want it to be easy to come on board to this project
5. **Experimentation** - We should work toward a solution that presents a different paradigm for how to work with data than that which is currently in use

## Considered Options

1. A fully custom-built infrastructure and solution

   1. Pros:
      1. **Simplicity** -- We can match our implementation to our needs directly
      2. **Experimentation** -- We could potentially arrive at a solution that is pretty different from what's there now
   2. Cons:
      1. **Duration** - This may result in this project taking longer
      2. **Coherence** we risk creating a cobbled together solution that does not handle data in a unified way
      3. **Precedent** - we do not benefit from previous solutions in this space

2. A traditional full RDBMS solution with stored procedures, using [SQL Server Integration Services](https://docs.microsoft.com/en-us/sql/integration-services/sql-server-integration-services?view=sql-server-ver15) to orchestrate jobs in a standard SQL Server DB

   1. Pros:
      1. **Precedent** - our STLT partners currently have a similar system; this is well-traveled ground
      2. **Coherence** - this is well-trod territory in data engineering
   2. Cons:
      1. **Experimentation** - this may not be different enough from the current way of processing data to be able to show the benefits of an alternative paradigm

3. Utilizing the infrastructure as outlined in [Data Engineering with Apache Spark, Delta Lake, and Lakehouse](https://www.packtpub.com/product/data-engineering-with-apache-spark-delta-lake-and-lakehouse/9781801077743) and its source code [here](https://github.com/PacktPublishing/Data-Engineering-with-Apache-Spark-Delta-Lake-and-Lakehouse),
   1. Pros:
      1. **Duration** - We can move quickly with a solution that has already made decisions for us
      2. **Simplicity** - This solution is ultimately data factory for ingest, a notebook for curation, and azure synapse for querying data, which is not too complicated
      3. **Coherence** - This book outlines an end-to-end solution that covers the path from raw to fully-processed data.
      4. **Precedent** - this is essentially the architecture that the CDC has adopted for [IZDL](https://www.cdc.gov/vaccines/covid-19/reporting/overview/IT-systems.html) and [Enterprise Data Analytics and Visualization](https://phii.org/wp-content/uploads/2021/10/Day1_KeynoteSlides_DanJernigan.pdf) platform, systems already in production that service a large volume of existing traffic
      5. **Experimentation** - This system is quite different from the current STLT systems we have worked most closely with
   2. Cons:
      1. **Precedent** - a more traditional SQL Server-based workflow is likely a bit more familiar to folks new to this space; also, we have parts of this wrokflow that don't map perfectly to the architecture in the book.

## Decision Outcome

Decision: Use the infrastructure from this book wherever possible; create experimentation tasks to try out this baseline and document deviations; conduct additional experiments to avoid blocking ourselves in.

1. **Part 1**: Wherever possible, we adopt the architecture outlined in [Data Engineering with Apache Spark, Delta Lake, and Lakehouse](https://www.packtpub.com/product/data-engineering-with-apache-spark-delta-lake-and-lakehouse/9781801077743) and its source code [here](https://github.com/PacktPublishing/Data-Engineering-with-Apache-Spark-Delta-Lake-and-Lakehouse), at least for the duration of this prototype. As seen above the benefits are significant and it addresses all five aspects of our decision drivers.
2. **Part 2**: We create tickets to attempt to perform actual work using this above infrastructure as a way of combining coming to understand it and also accomplishing some task. Where it is deficient, we conclude this following implementation and decide together on an alternative. Where the provided-architecture doesn’t match our work -- namely around FHIR and adopting the Microsoft Common Data Model (though there is some overlap) -- we also create task-specific “spike+” tickets that combine investigation and implementation. Also, wherever possible defer to official documentation and seek to minimize proprietary and custom architectures
3. **Part 3**: In order to avoid tying ourselves too closely to the particulars of the architecture from (1) longer term, we occasionally perform small, contained proof of concept tickets such as those around data orchestration in this current sprint as a means of deciding between alternatives.

## Appendix

See above links
