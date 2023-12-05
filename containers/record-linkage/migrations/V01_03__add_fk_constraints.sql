BEGIN;

/* 

ADD FOREIGN KEY CONSTRAINTS BACK

*/
ALTER TABLE name ADD CONSTRAINT fk_name_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id);

ALTER TABLE identifier ADD CONSTRAINT fk_ident_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id);

ALTER TABLE phone_number ADD CONSTRAINT fk_phone_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id);

ALTER TABLE address ADD CONSTRAINT fk_addr_to_patient 
FOREIGN KEY (patient_id)
REFERENCES patient(patient_id);

ALTER TABLE given_name ADD CONSTRAINT fk_given_to_name 
FOREIGN KEY (name_id)
REFERENCES name(name_id);

ALTER TABLE external_person ADD CONSTRAINT fk_ext_person_to_person 
FOREIGN KEY (person_id)
REFERENCES person(person_id);

ALTER TABLE external_person ADD CONSTRAINT fk_ext_person_to_source 
FOREIGN KEY (external_source_id)
REFERENCES external_source(external_source_id);



COMMIT;
 