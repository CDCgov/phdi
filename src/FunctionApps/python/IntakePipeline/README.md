# Intake Pipeline Function App

## Config

This function app requires some config to be present. In production this is defined on the function app, and locally, you'll want to add
items in `local.settings.json` under `Values`.

* `INTAKE_CONTAINER_URL`: a container URL containing ndjson formatted FHIR records (eg: https://pitestdatasa.blob.core.windows.net/bronze)
* `INTAKE_CONTAINER_PREFIX`: a string prefix so we're not scanning the entire container (eg: decrypted/valid-messages)
* `SMARTYSTREETS_AUTH_ID`: an auth id used in geocoding
* `SMARTYSTREETS_AUTH_TOKEN`: the corresponding auth token
* `HASH_SALT`: a salt to use when hashing the patient identifier
