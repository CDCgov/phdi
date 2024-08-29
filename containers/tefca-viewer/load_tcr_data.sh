#!/bin/bash

source tefca.env

# Define the database connection string using environment variables
PG_CONN="postgresql://postgres:pw@db:5432/tefca_db"

tables=("concepts" "valuesets" "conditions")

### TEMP: Remove this once flyway is implemented
for table in "${tables[@]}"; do
    psql "$PG_CONN" -c "CREATE TABLE IF NOT EXISTS $table (id INT, name VARCHAR(80));" -tA
    echo "Table $table created."
    pgsl "$PG_CONN" -c "INSERT INTO $table (id, name) VALUES (1, item);"
done
### END TEMP

# Function to check if tables contain data
check_tables() {
  for table in "${tables[@]}"; do
    count=$(psql "$PG_CONN" -c "SELECT COUNT(*) FROM $table;" -tA)
    if [ "$count" -eq 0 ]; then
      return 1
    fi
  done
  return 0
}

# Check if the tables contain data
check_tables
if [ $? -ne 0 ]; then
  echo "Tables are empty. Proceeding with data loading..."

  # Install pgloader if not already installed
  if ! command -v pgloader &> /dev/null; then
    echo "Installing pgloader..."
    apk add --no-cache pgloader
  fi

  # Download the ERSD SQLite file
  echo "Downloading ERSD SQLite file..."
  wget -O /tmp/ersd.db https://github.com/CDCgov/phdi/raw/main/containers/trigger-code-reference/seed-scripts/ersd.db

  echo "Loading data into PostgreSQL..."
  pgloader sqlite://tmp/ersd.db "$PG_CONN"

  echo "Successfully loaded TCR data into tefca_db"

fi
