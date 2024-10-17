-- ./seed-scripts/init.sql

CREATE TABLE IF NOT EXISTS fhir (
  ecr_id VARCHAR(200) NOT NULL,
  data JSONB NOT NULL,
  date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (ecr_id)
);