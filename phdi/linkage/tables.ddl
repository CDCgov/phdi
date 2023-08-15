USE DibbsMpiDB;

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS patient (
    patient_id  UUID DEFAULT uuid_generate_v4 ()
    person_id   UUID
    patient_resource JSONB
    PRIMARY KEY (patient_id)
);

CREATE TABLE IF NOT EXISTS person (
    person_id   UUID DEFAULT uuid_generate_v4 () 
    PRIMARY KEY (person_id)
);

CREATE TABLE IF NOT EXISTS external_sources (
    external_source_key   UUID DEFAULT uuid_generate_v4 () 
    external_source_name    VARCHAR(100)
    external_source_description     VARCHAR(500)
    PRIMARY KEY (external_source_key)
);

CREATE TABLE IF NOT EXISTS external_person_ids (
    external_id_key   UUID DEFAULT uuid_generate_v4 () 
    person_id   UUID
    external_person_id   VARCHAR(100)
    external_source_key   UUID
    PRIMARY KEY (external_id_key)
);

COMMIT;