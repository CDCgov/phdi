BEGIN;

/* 

Drop the old constraints, if they exist, and then recreate them with the DEFERRABLE INITIALLY DEFERRED option.

*/
ALTER TABLE name DROP CONSTRAINT IF EXISTS fk_name_to_patient;

ALTER TABLE name ADD CONSTRAINT fk_name_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE identifier DROP CONSTRAINT IF EXISTS fk_ident_to_patient;

ALTER TABLE identifier ADD CONSTRAINT fk_ident_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE phone_number DROP CONSTRAINT IF EXISTS fk_phone_to_patient;

ALTER TABLE phone_number ADD CONSTRAINT fk_phone_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE address DROP CONSTRAINT IF EXISTS fk_addr_to_patient;

ALTER TABLE address ADD CONSTRAINT fk_addr_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE given_name DROP CONSTRAINT IF EXISTS fk_given_to_name;

ALTER TABLE given_name ADD CONSTRAINT fk_given_to_name 
FOREIGN KEY (name_id)
REFERENCES name(name_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE external_person DROP CONSTRAINT IF EXISTS fk_ext_person_to_person;

ALTER TABLE external_person ADD CONSTRAINT fk_ext_person_to_person 
FOREIGN KEY (person_id)
REFERENCES person(person_id)
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE external_person DROP CONSTRAINT IF EXISTS fk_ext_person_to_source;

ALTER TABLE external_person ADD CONSTRAINT fk_ext_person_to_source 
FOREIGN KEY (external_source_id)
REFERENCES external_source(external_source_id)
DEFERRABLE INITIALLY DEFERRED;

COMMIT;
 