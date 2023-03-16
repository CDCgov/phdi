USE DibbsMpiDB;
BEGIN;
CREATE TABLE IF NOT EXISTS patient (
    patient_id  VARCHAR(32) PRIMARY KEY
    person_id   VARCHAR(32) FOREIGN KEY
    name    JSONB
    sex ENUM ('male', 'female', 'other', 'unknown')
    birthdate   DATE
    telecom JSONB
    identifier  JSONB
    address JSONB
);

CREATE TABLE IF NOT EXISTS person (
    person_id   VARCHAR(32) PRIMARY KEY
    external_person_id  VARCHAR(64)
);
COMMIT;