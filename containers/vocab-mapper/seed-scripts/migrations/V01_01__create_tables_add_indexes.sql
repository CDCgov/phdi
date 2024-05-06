-- create tables to link conditions to clinical services
CREATE TABLE IF NOT EXISTS value_set_type (
    id TEXT PRIMARY KEY,
    clinical_service_type TEXT
);

CREATE TABLE IF NOT EXISTS value_sets (
    id TEXT PRIMARY KEY,
    version TEXT,
    value_set_name TEXT,
    author TEXT,
    clinical_service_type_id TEXT,
    FOREIGN KEY (clinical_service_type_id) REFERENCES value_set_type(id)
);

CREATE TABLE IF NOT EXISTS conditions (
    id TEXT,
    value_set_id TEXT,
    system TEXT,
    name TEXT,
    FOREIGN KEY (value_set_id) REFERENCES value_sets(id)
);

CREATE TABLE IF NOT EXISTS clinical_services (
    id TEXT PRIMARY KEY,
    value_set_id TEXT,
    code TEXT,
    code_system TEXT,
    display TEXT,
    version TEXT,
    FOREIGN KEY (value_set_id) REFERENCES value_sets(id)
);

-- add indexes to increase performance
-- conditions
CREATE INDEX IF NOT EXISTS "idx_conditions_id" ON conditions(id);
CREATE INDEX IF NOT EXISTS "idx_conditions_value_set_id" ON conditions(value_set_id);

-- value_sets
CREATE INDEX IF NOT EXISTS "idx_value_sets_id" ON value_sets(id);
CREATE INDEX IF NOT EXISTS "idx_value_sets_clinical_service_type_id" ON value_sets(clinical_service_type_id);

-- value_set_type
CREATE INDEX IF NOT EXISTS "idx_value_set_type_id" ON value_set_type(id);

-- clinical_services
CREATE INDEX IF NOT EXISTS "idx_clinical_services_id" ON clinical_services(id);
CREATE INDEX IF NOT EXISTS "idx_clinical_services_value_set_id" ON clinical_services(value_set_id);
