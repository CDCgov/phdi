#!/bin/bash

RESET_DIR=${LIB_DIR:-/usr/local/lib}

# Read the contents of another file for a value
VALUE_FROM_FILE=$(cat $RESET_DIR/example_eicr_with_rr_data_with_person.json)

# Replace placeholders in the template.sql file with actual values
echo "reset dir"
echo $RESET_DIR
sed "s~{{VALUE1}}~$VALUE_FROM_FILE~g" "$RESET_DIR/insert_fhir_bundle.sql" > "$RESET_DIR/output.sql"

# Run the modified SQL script
# psql postgres://postgres:pw@localhost:5432/ecr_viewer_db  -f $RESET_DIR/output.sql
psql -v ON_ERROR_STOP=1  -U "postgres" ecr_viewer_db -f "$RESET_DIR/output.sql"
