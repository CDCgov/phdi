#!/bin/bash

# Define the certificate and key file locations
CERT_FILE=/var/lib/postgresql/server.crt
KEY_FILE=/var/lib/postgresql/server.key

# Check if the certificate and key files already exist
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  echo "Generating new SSL certificate and key..."
  
  # Generate the SSL certificate and key
  openssl req -new -x509 -days 365 -nodes -out $CERT_FILE -keyout $KEY_FILE -subj "/CN=localhost"
  
  # Ensure correct permissions for the key file
  chmod og-rwx $KEY_FILE
fi

# Start PostgreSQL with SSL enabled
exec postgres -c ssl=on \
              -c ssl_cert_file=$CERT_FILE \
              -c ssl_key_file=$KEY_FILE
