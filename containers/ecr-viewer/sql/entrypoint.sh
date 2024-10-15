#!/bin/bash

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to start (you can fine-tune the sleep time if needed)
sleep 120

# Run the setup script to create the DB and the schema in the DB
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD -d master -i /var/opt/mssql/scripts/extended.sql -C

# Bring SQL Server to the foreground to keep the container running
wait