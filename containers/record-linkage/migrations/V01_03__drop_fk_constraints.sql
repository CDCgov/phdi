BEGIN;

/* 
REMOVE FOREIGN KEY CONSTRAINTS
*/
ALTER TABLE address DROP CONSTRAINT fk_addr_to_patient;

ALTER TABLE phone_number DROP CONSTRAINT fk_phone_to_patient;

ALTER TABLE identifier DROP CONSTRAINT fk_ident_to_patient;

ALTER TABLE name DROP CONSTRAINT fk_name_to_patient;

ALTER TABLE given_name DROP CONSTRAINT fk_given_to_name;

ALTER TABLE external_person DROP CONSTRAINT fk_ext_person_to_source;

ALTER TABLE external_person DROP CONSTRAINT fk_ext_person_to_person;