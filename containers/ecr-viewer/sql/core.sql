CREATE TABLE IF NOT EXISTS ecr_data
(
  ecr_id VARCHAR(200) NOT NULL,
  data_source VARCHAR(2) NOT NULL, -- S3 or DB
  data_link VARCHAR(500), -- Link to the data
  patient_name_first VARCHAR(100) NOT NULL,
  patient_name_last VARCHAR(100) NOT NULL,
  patient_birth_date DATE NOT NULL,
  report_date DATE,
  PRIMARY KEY (ecr_id)
);