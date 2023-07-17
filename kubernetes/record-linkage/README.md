# Record Linkage
Visit the [record linkage documentation](https://cdcgov.github.io/phdi/latest/containers/record-linkage.html) for information on ways to use this service, including available endpoints.

## Running the service
This Helm chart assumes you have an external database running for the Master Patient Index. The service won't work without it.

You can [run a database locally](https://github.com/CDCgov/phdi/wiki/Testing-the-SDK-Locally#setting-up-your-test-mpi-database-for-record-linkage-testing) using the default Docker Postgres image, or use a managed Postgres database from the cloud provider of your choice.

The record linkage service applies the appropriate table schema to the MPI as it's starting up, so you don't need to apply the table configuration manually.