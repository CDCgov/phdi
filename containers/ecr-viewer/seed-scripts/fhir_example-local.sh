#!/bin/bash


VALUE_FROM_FILE=$(cat ./example_eicr_with_rr_data_with_person.json)

ESCAPED_TEXT=$(echo -e "$VALUE_FROM_FILE" | sed ':a;N;$!ba;s/\n/\\n/g')

sed "s|{{VALUE1}}|$ESCAPED_TEXT|g" "./insert_fhir_bundle.sql" > "./output.sql"
