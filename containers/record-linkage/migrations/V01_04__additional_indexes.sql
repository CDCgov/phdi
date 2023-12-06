BEGIN;

/* 

Additional Indexes for identifier type and given name index.

*/

CREATE INDEX IF NOT EXISTS identifier_type_index ON identifier (type_code);

CREATE INDEX IF NOT EXISTS given_name_index_index ON given_name (given_name_index);

COMMIT;
