# CSV Generator Function App

## Config

This function app requires config to be present. Locally these are settings in `local.settings.json`, and in production they'll be defined under the configuration tab

* `CONTAINER_URL`: a container URL with FHIR formatted records (eg: https://pitesetdatasa.blob.core.windows.net/bronze)
* `CSV_OUTPUT_PREFIX`: a path for the output CSVs to be written
