# FHIR API Exporter

This provides an endpoint that exports the FHIR data into a blob storage container defined on the FHIR server instance.

The function kicks off an export and then polls the status endpoint until it finished (or it's been five minutes).

## Environment Config

* `CLIENT_ID` - the Azure client id
* `CLIENT_SECRET` - the corresponding secret
* `FHIR_URL` - the base url for the FHIR API server, without a trailing slash
* `TENANT_ID` - the tenant id for the Azure account

If you're just getting started, someone can probably send these via Keybase.
