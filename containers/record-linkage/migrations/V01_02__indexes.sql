BEGIN;

/* 

FOREIGN KEY INDEXES

Postgres does not automatically create indexes for foreign keys. 
Testing has shown that indexing foreign keys improves performance by 10x or more.

*/
CREATE INDEX IF NOT EXISTS address_patient_id_index ON address (patient_id);

CREATE INDEX IF NOT EXISTS identifier_patient_id_index ON identifier (patient_id);

CREATE INDEX IF NOT EXISTS name_patient_id_index ON name (patient_id);

CREATE INDEX IF NOT EXISTS given_name_name_id_index ON given_name (name_id);

CREATE INDEX IF NOT EXISTS phone_number_patient_id_index ON phone_number (patient_id);

CREATE INDEX IF NOT EXISTS patient_person_id_index ON patient (person_id);

CREATE INDEX IF NOT EXISTS external_person_person_id_index ON external_person (person_id);

CREATE INDEX IF NOT EXISTS external_person_external_source_id_index ON external_person (external_source_id);

/* 

BLOCKING INDEXES 

Indexing by the filter conditions for each block improves performance.

*/

-- Block 1 - First 4 characters of address and last 4 characters of MRN
CREATE INDEX IF NOT EXISTS address_line_1_index ON address (left(line_1, 4));

CREATE INDEX IF NOT EXISTS identifier_value_and_type_code_index ON identifier (right(patient_identifier, 4), type_code);

-- Block 2 - First 4 characters of last name and first 4 characters of first name
CREATE INDEX IF NOT EXISTS name_last_name_index ON name (left(last_name, 4));

CREATE INDEX IF NOT EXISTS given_name_given_name_index ON given_name (left(given_name, 4));

COMMIT;
