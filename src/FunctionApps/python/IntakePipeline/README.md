# Intake Pipeline Function App

## Config

This function app module requires some config to be present. In production this is defined on the function app, and locally, you'll want to add
items in `local.settings.json` under `Values`.

* `INTAKE_CONTAINER_URL`: a container URL containing FHIR bundles (eg: https://pitestdatasa.blob.core.windows.net/bronze)\
    * Stored bundles must be of type `batch`.  Entries in the batch Bundle should contain a valid `request` describing how the `resource` should be submitted to the FHIR Server.
* `INTAKE_CONTAINER_PREFIX`: a string prefix so we're not scanning the entire container (eg: decrypted/valid-messages/)\
    * Assuming prefixes are a complete directory path, prefixes should have a trailing /.  Also, there must be a sub-structure of record types (all caps) under the prefix (eg: decrypted/valid-messages/VXU).
* `OUTPUT_CONTAINER_PATH`: the blob container path to store processed items (eg: test-out)\
    * Do not include a trailing /.
* `SMARTYSTREETS_AUTH_ID`: an auth id used in geocoding
* `SMARTYSTREETS_AUTH_TOKEN`: the corresponding auth token
* `HASH_SALT`: a salt to use when hashing the patient identifier
* `FHIR_URL`: the base url for the FHIR server used to persist FHIR objects
