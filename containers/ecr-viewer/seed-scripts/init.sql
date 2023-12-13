-- ./seed-scripts/init.sql

CREATE TABLE IF NOT EXISTS fhir (
  ecr_id VARCHAR NOT NULL,
  data JSONB NOT NULL,
  PRIMARY KEY (ecr_id)
);