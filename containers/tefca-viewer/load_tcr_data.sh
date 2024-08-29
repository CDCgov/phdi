#!/bin/bash

source tefca.env

# Define the database connection string using environment variables
PG_CONN="postgresql://postgres:pw@db:5432/tefca_db"

echo "PG_CONN: $PG_CONN"

# Function to check if the "concepts" table contains data
check_concepts_table() {
  psql "CREATE TABLE concepts (id TEXT PRIMARY KEY, name TEXT NOT NULL);"
  count=$(psql "$PG_CONN" -c "SELECT COUNT(*) FROM concepts;" -tA)
  if [ "$count" -eq 0 ]; then
    return 1  # Table is empty
  else
    return 0  # Table contains data
  fi
}

# Check if the "concepts" table contains data
check_concepts_table