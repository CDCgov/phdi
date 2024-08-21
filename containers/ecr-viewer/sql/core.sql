CREATE TABLE ecr_data (
  eICR_ID VARCHAR(200) NOT NULL,
  data_source VARCHAR(2) NOT NULL, -- S3 or DB
  data_link VARCHAR(500), -- Link to the data
  patient_name_first VARCHAR(100) NOT NULL,
  patient_name_last VARCHAR(100) NOT NULL,
  patient_birth_date DATE NOT NULL,
  report_date DATE,
  PRIMARY KEY (eICR_ID)
);

CREATE TABLE ecr_rr_conditions (
    uuid UUID PRIMARY KEY,
    eICR_ID VARCHAR(200) NOT NULL REFERENCES ecr_data(eICR_ID),
    condition VARCHAR(255)
);

CREATE TABLE ecr_rr_rule_summaries (
    uuid UUID PRIMARY KEY,
    ecr_rr_conditions_id UUID REFERENCES ecr_rr_conditions(uuid),
    rule_summary TEXT
);