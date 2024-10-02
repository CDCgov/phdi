#!/bin/sh

mkdir -p /var/lib/postgresql/certs

openssl req -new -x509 -nodes -days 365 \
  -keyout /var/lib/postgresql/certs/server.key \
  -out /var/lib/postgresql/certs/server.crt \
  -subj "/CN=localhost"

chmod 600 /var/lib/postgresql/certs/server.key
chmod 644 /var/lib/postgresql/certs/server.crt
