-- ./seed-scripts/init.sql

CREATE TABLE IF NOT EXISTS fhir (
  ecr_id VARCHAR(200) NOT NULL,
  data JSONB NOT NULL,
  date_created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (ecr_id)
);

CREATE TABLE IF NOT EXISTS fhir_metadata(
  ecr_id VARCHAR(200) NOT NULL,
  data_source VARCHAR(2) NOT NULL, -- S3 or DB
  data_link VARCHAR(500), -- Link to the data
  patient_name_first VARCHAR(100) NOT NULL,
  patient_name_last VARCHAR(100) NOT NULL,
  patient_birth_date DATE NOT NULL,
  reportable_condition VARCHAR(10000),
  rule_summary VARCHAR(10000),
  report_date DATE,
  PRIMARY KEY (ecr_id)
)
