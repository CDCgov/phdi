-- ./seed-scripts/init.sql

CREATE TABLE IF NOT EXISTS fhir (
  ecr_id VARCHAR NOT NULL,
  data JSONB NOT NULL,
  PRIMARY KEY (ecr_id)
);


INSERT INTO fhir (ecr_id, data)
VALUES ('123', '{"my_fhir": "bundle"}');