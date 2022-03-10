# RFC Transition from Bronze to Silver Tier

This represents a basic function app to transform exported FHIR data in ndjson format by:

* Standardizing name
* Standardizing phone
* Geocoding addresses


## Environment Vars

These can be specified in `local.settings.json` to help boot a local version via `func start`

* `AZURE_STORAGE_CONNECTION_STRING` - the connection string for the storage account containing the bronze and silver containers
* `BRONZE_PATIENT_CONTAINER` - name of a container with exported FHIR data
* `SILVER_PATIENT_CONTAINER` - output container name
* `SMARTYSTREETS_AUTH_ID`
* `SMARTYSTREETS_AUTH_TOKEN`
* `COSMOSDB_CONN_STRING` - CosmosDB connection string for cached geocoding (can be left off if a local mongodb instance is running)
