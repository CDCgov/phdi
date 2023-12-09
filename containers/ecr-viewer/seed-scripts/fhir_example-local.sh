#!/bin/bash


VALUE_FROM_FILE=$(cat ./example_eicr_with_rr_data_with_person.json)

CLEAN_FHIR=$(echo "$VALUE_FROM_FILE" | jq -c .)
NO_APOSTROPHE=$(echo $CLEAN_FHIR | tr -d "'")

sed "s|{{VALUE1}}|$NO_APOSTROPHE|g" "./insert_fhir_bundle.sql" > "./output.sql"
