#!/bin/bash

# Check if tefca-fhir-server is up
while ! curl -s http://tefca-fhir-server:8080/fhir/ > /dev/null

# POST Bundle of synthetic data to spun up server

curl -X POST -H "Content-Type: application/json" -d @/etc/BundleHAPIServer.json http://tefca-fhir-server:8080/fhir/
