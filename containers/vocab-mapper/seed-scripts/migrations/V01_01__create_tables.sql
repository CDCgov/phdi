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