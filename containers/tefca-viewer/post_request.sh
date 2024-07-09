#!/bin/bash

sleep 120 #TODO: Change to wait for positive response instead of hardcoding time

curl -X POST -H "Content-Type: application/json" -d @/etc/BundleHAPIServer.json http://tefca-fhir-server:8080/fhir/



# sleep 180
