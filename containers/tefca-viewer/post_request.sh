#!/bin/bash

# URL to check
URL="http://tefca-fhir-server:8080/fhir/"
TEST_URL="http://tefca-fhir-server:8080/fhir/metadata"

# Maximum number of attempts (120 seconds / 5 seconds = 24 attempts)
MAX_ATTEMPTS=24

# Counter for attempts
attempt=0

# Loop to check server health
while [ $attempt -lt $MAX_ATTEMPTS ]; do
    # Perform the curl request
    response=$(curl -s -o /dev/null -w "%{http_code}" $TEST_URL)
    
    # Check if the response is 200 (OK)
    if [ $response -eq 200 ]; then
        echo "Server is healthy!"
        
        # POST Bundle of synthetic data to spun up server
        curl -X POST -H "Content-Type: application/json" -d @/etc/BundleHAPIServer.json $URL
        
        exit 0
    fi
    
    attempt=$((attempt + 1))
    
    sleep 5
done

echo "Server is not healthy after 120 seconds."
exit 1