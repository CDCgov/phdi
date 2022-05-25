# Introduction
This file contains functionality and configuration descriptions for the FhirServerExport Azure function.

# Function App Settings
This function app module requires some config to be present. In production this is defined on the Function App Azure Resource in the Settings screen.  Locally, configuration is stored in `local.settings.json` under `Values`.

* Cloud Settings Documentation: https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings
* Local Settings Documentation: https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local#local-settings-file

The configuration values required to be set for the IntakePipeline function are described below.

* `FHIR_URL`: the base url for the FHIR server used to persist FHIR objects
* `FHIR_EXPORT_POLL_INTERVAL`: (default = 30) the number of seconds to wait between checks for the completion of an export.  This setting supports a decimal value.
* `FHIR_EXPORT_POLL_TIMEOUT`: (default = 300) the number of seconds to wait for the completion of an export.  If the time extends beyond this interval, the function will return a timeout error.
* `FHIR_EXPORT_CONTAINER`: (default = "fhir-exports") the name of the container that holds export runs (the service account is configured in the FHIR Server).  In order to create a new container for each export run, enter a value of `<none>`.  

# Description
This function provides a simplified client to the Azure implementation of the [HL7 Bulk Data Export](https://hl7.org/fhir/uv/bulkdata/export/index.html) specification.  The [Azure implementation](https://docs.microsoft.com/en-us/azure/healthcare-apis/fhir/export-data) follows the general guidance outlined by the spec, but is tied to Azure in that it stores exported files to Blob storage.  

## HTTP Trigger Request Specification
The HTTP trigger accepts the following query parameters:
* `export_scope`: Supported scopes include system level (default behavior), patient level ("Patient"), and Group Level ("Group/\[id\]").  Details are described in more detail in the [Azure export documentation](https://docs.microsoft.com/en-us/azure/healthcare-apis/fhir/export-data#using-export-command) and [HL7 Bulk Export documentation](https://hl7.org/fhir/uv/bulkdata/export/index.html#bulk-data-kick-off-request)
* `since`: Allows you to specify a [FHIR instant formatted](https://build.fhir.org/datatypes.html#instant) value.  This will limit the exported data to records which have been created or modified since the specified date.
* `type`: Allows you to specify a comma-separated list of FHIR resource types to export.  If set, unlisted types will not be included in the exported.  Default behavior is to export all types.

## FHIR Server Export Process
The process is described in detail by the HL7 Bulk Data Export specification and Azure Implementation linked above.  A summary explanation is outlined below.
* *Kick-off request*: An initial request is made to the server to initiate the export process within the FHIR server.  Parameters described in the HTTP Trigger Request Specification section above are used in the kick-off request to control the scope of the exported information.  
* *Polling requests*: After the kick-off request is made, the FHIR server will return immediate and include a polling URL in the HTTP response headers.  Meanwhile, it will kick off an asynchronous job that collects information from the FHIR server and exports it to blob storage.  This process may take some time.  The function will poll the provided URL using the `FHIR_EXPORT_POLL_INTERVAL` and `FHIR_EXPORT_POLL_TIMEOUT` Azure Function App settings until it returns a 200 response, indicating the export files are finished and ready to be downloaded.  This final response will include a list of blob files to be downloaded.
