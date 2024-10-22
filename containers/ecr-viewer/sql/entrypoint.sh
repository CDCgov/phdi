#!/bin/bash

/opt/mssql/bin/sqlservr &

/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD -d master -i /var/opt/mssql/scripts/extended.sql -C

wait