#!/bin/bash

BASEDIR=$(dirname "$0")

echo "Installing JQ"
if brew list jq &>/dev/null; then
    echo "JQ is already installed"
else
    brew install jq && echo "JQ is installed"
fi


echo "Starting fhir-converter"
docker run --rm -d -it -p 8080:8080 $(docker build -q $BASEDIR/../../fhir-converter/)

echo "Looping through folders in baseECR"
for d in "$BASEDIR"/baseECR/* ; do
    #first escape ", then /, and finally remove all new lines
    rr=$(sed -e 's/"/\\"/g ; s=/=\\\/=g ; $!s/$/\\n/' "$d/CDA_RR.xml" | tr -d '\n')
    eicr=$(sed 's/"/\\"/g ; s=/=\\\/=g ; $!s/$/\\n/'  "$d/CDA_eICR.xml" | tr -d '\n')
    resp=$(curl -l 'http://localhost:8080/convert-to-fhir' --header 'Content-Type: application/json' --data-raw '{"input_type":"ecr","root_template":"EICR","input_data": "'"$eicr"'","rr_data": "'"$rr"'"}')
    echo $resp | jq '.response.FhirResource' > "$BASEDIR/fhir_data/$(basename $d).json"

done
