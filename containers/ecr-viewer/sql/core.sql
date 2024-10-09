CREATE TABLE ecr_data (
  eICR_ID VARCHAR(200) PRIMARY KEY,
  data_source VARCHAR(2), -- S3 or DB
  fhir_reference_link VARCHAR(500), -- Link to the ecr fhir bundle
  patient_name_first VARCHAR(100),
  patient_name_last VARCHAR(100),
  patient_birth_date DATE,
  report_date DATE
);

CREATE TABLE ecr_rr_conditions (
    uuid VARCHAR(200) PRIMARY KEY,
    eICR_ID VARCHAR(200) NOT NULL REFERENCES ecr_data(eICR_ID),
    condition VARCHAR
);

CREATE TABLE ecr_rr_rule_summaries (
    uuid VARCHAR(200) PRIMARY KEY,
    ecr_rr_conditions_id VARCHAR(200) REFERENCES ecr_rr_conditions(uuid),
    rule_summary VARCHAR
);