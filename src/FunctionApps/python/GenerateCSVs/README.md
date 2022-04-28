# CSV Generator Function App

## Config

This function app requires config to be present. Locally these are settings in `local.settings.json`, and in production they'll be defined under the configuration tab

* `CONTAINER_URL`: a container URL containing FHIR bundles to be converted to CSV (eg: https://pitestdatasa.blob.core.windows.net/bronze)
* `CSV_INPUT_PREFIX`: a string prefix where FHIR bundles are stored within the container
    * Assuming prefixes are a complete directory path, prefixes should have a trailing /.  
    * There must be a sub-structure of record types (all caps) under the prefix (eg: `[CSV_INPUT_PREFIX]`VXU, `[CSV_INPUT_PREFIX]`ELR)
* `CSV_OUTPUT_PREFIX`: a string prefix where FHIR CSV output files are stored within the container
    * Do not include a trailing /.

## Running via CLI

Run `generate_csvs.py` from the python function root via something like:

```
python generate_csvs.py "https://pitestdatasa.blob.core.windows.net/bronze" "blob-trigger-out/valid-messages/" vxu > /tmp/vxu.csv"
```

and wait a very, very long time. If you want to see the csv being built, try

```
tail -f /tmp/vxu.csv
```

in another terminal.
