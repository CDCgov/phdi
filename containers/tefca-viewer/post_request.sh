#!/bin/bash

sleep 120

curl -X POST -H "Content-Type: application/json" -d @/etc/BundleHAPIServer.json http://tefca-fhir-server:8080/fhir/



# sleep 180
