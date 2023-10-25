BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS person (
    person_id UUID DEFAULT uuid_generate_v4 (),
    PRIMARY KEY (person_id)
);

CREATE TABLE IF NOT EXISTS patient (
    patient_id UUID DEFAULT uuid_generate_v4 (),
    person_id UUID,
    dob DATE,
    sex VARCHAR(7),
    race VARCHAR(100),
    ethnicity VARCHAR(100),
    PRIMARY KEY (patient_id),
    CONSTRAINT fk_patient_to_person FOREIGN KEY(person_id) REFERENCES person(person_id)
);

CREATE TABLE IF NOT EXISTS name (
    name_id UUID DEFAULT uuid_generate_v4 (),
    patient_id UUID,
    last_name VARCHAR(255),
    type VARCHAR(100),
    PRIMARY KEY (name_id),
    CONSTRAINT fk_name_to_patient FOREIGN KEY(patient_id) REFERENCES patient(patient_id)
);

CREATE TABLE IF NOT EXISTS given_name (
    given_name_id UUID DEFAULT uuid_generate_v4 (),
    name_id UUID,
    given_name VARCHAR(255),
    given_name_index INTEGER,
    PRIMARY KEY (given_name_id),
    CONSTRAINT fk_given_to_name FOREIGN KEY(name_id) REFERENCES name(name_id)
);

CREATE TABLE IF NOT EXISTS identifier (
    identifier_id UUID DEFAULT uuid_generate_v4 (),
    patient_id UUID,
    patient_identifier VARCHAR(255),
    type_code VARCHAR(255),
    type_display VARCHAR(255),
    type_system VARCHAR(255),
    PRIMARY KEY (identifier_id),
    CONSTRAINT fk_ident_to_patient FOREIGN KEY(patient_id) REFERENCES patient(patient_id)
);

CREATE TABLE IF NOT EXISTS phone_number (
    phone_id UUID DEFAULT uuid_generate_v4 (),
    patient_id UUID,
    phone_number VARCHAR(20),
    type VARCHAR(100),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    PRIMARY KEY (phone_id),
    CONSTRAINT fk_phone_to_patient FOREIGN KEY(patient_id) REFERENCES patient(patient_id)
);

CREATE TABLE IF NOT EXISTS address (
    address_id UUID DEFAULT uuid_generate_v4 (),
    patient_id UUID,
    type VARCHAR(100),
    line_1 VARCHAR(100),
    line_2 VARCHAR(100),
    city VARCHAR(255),
    zip_code VARCHAR(10),
    state VARCHAR(100),
    country VARCHAR(255),
    latitude DECIMAL,
    longitude DECIMAL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    PRIMARY KEY (address_id),
    CONSTRAINT fk_addr_to_patient FOREIGN KEY(patient_id) REFERENCES patient(patient_id)
);

CREATE TABLE IF NOT EXISTS external_source (
    external_source_id UUID DEFAULT uuid_generate_v4 (),
    external_source_name VARCHAR(255),
    external_source_description VARCHAR(255),
    PRIMARY KEY (external_source_id)
);

CREATE TABLE IF NOT EXISTS external_person (
    external_id UUID DEFAULT uuid_generate_v4 (),
    person_id UUID,
    external_person_id VARCHAR(255),
    external_source_id UUID,
    PRIMARY KEY (external_id),
    CONSTRAINT fk_ext_person_to_person FOREIGN KEY(person_id) REFERENCES person(person_id),
    CONSTRAINT fk_ext_person_to_source FOREIGN KEY(external_source_id) REFERENCES external_source(external_source_id)
);

COMMIT;

INSERT INTO external_source (external_source_id, external_source_name, external_source_description)
VALUES ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380b79','IRIS','LACDPH Surveillance System');
COMMIT;
