USE DibbsMpiDB;
BEGIN;
CREATE TABLE IF NOT EXISTS patient (
    patient_id  UUID DEFAULT uuid_generate_v4 ()
    person_id   VARCHAR(32) FOREIGN KEY
    patient_resource JSONB
    PRIMARY KEY (patient_id)
);

CREATE TABLE IF NOT EXISTS person (
    person_id   UUID DEFAULT uuid_generate_v4 () 
    external_person_id  VARCHAR(100)
    PRIMARY KEY (person_id)
);
COMMIT;