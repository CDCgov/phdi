BEGIN;

/* 
REMOVE FOREIGN KEY CONSTRAINTS
*/
ALTER TABLE address DROP CONSTRAINT IF EXISTS fk_addr_to_patient;

ALTER TABLE phone_number DROP CONSTRAINT IF EXISTS fk_phone_to_patient;

ALTER TABLE identifier DROP CONSTRAINT IF EXISTS fk_ident_to_patient;

ALTER TABLE name DROP CONSTRAINT IF EXISTS fk_name_to_patient;

ALTER TABLE given_name DROP CONSTRAINT IF EXISTS fk_given_to_name;

ALTER TABLE external_person DROP CONSTRAINT IF EXISTS fk_ext_person_to_source;

ALTER TABLE external_person DROP CONSTRAINT IF EXISTS fk_ext_person_to_person;

COMMIT;