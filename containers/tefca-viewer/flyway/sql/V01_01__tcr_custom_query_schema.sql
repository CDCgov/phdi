CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS conditions (
    id TEXT PRIMARY KEY,
    system TEXT,
    name TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS valuesets (
    id TEXT PRIMARY KEY,
    oid TEXT,
    version TEXT,
    name TEXT,
    author TEXT,
    type TEXT
);

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    code TEXT,
    code_system TEXT,
    display TEXT,
    gem_formatted_code TEXT,
    version TEXT
);

CREATE TABLE IF NOT EXISTS condition_to_valueset (
    id TEXT PRIMARY KEY,
    condition_id TEXT,
    valueset_id TEXT,
    source TEXT,
    FOREIGN KEY (condition_id) REFERENCES conditions(id),
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id)
);

CREATE TABLE IF NOT EXISTS valueset_to_concept (
    id TEXT PRIMARY KEY,
    valueset_id TEXT,
    concept_id TEXT,
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

CREATE TABLE IF NOT EXISTS icd_crosswalk (
    id TEXT PRIMARY KEY,
    icd10_code TEXT,
    icd9_code TEXT,
    match_flags TEXT);


CREATE TABLE IF NOT EXISTS query (
    id UUID DEFAULT uuid_generate_v4 (),
    query_name VARCHAR(255),
    author VARCHAR(255),
    date_created TIMESTAMP,
    date_last_modified TIMESTAMP,
    time_window_number INT,
    time_window_unit VARCHAR(80),
    PRIMARY KEY (id));

CREATE TABLE IF NOT EXISTS query_to_valueset (
    id TEXT PRIMARY KEY,
    query_id UUID,
    valueset_id TEXT,
    valueset_oid TEXT,
    FOREIGN KEY (query_id) REFERENCES query(id),
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id)
);

CREATE TABLE IF NOT EXISTS query_included_concepts (
    id TEXT PRIMARY KEY,
    query_by_valueset_id TEXT,
    concept_id TEXT,
    include BOOLEAN,
    FOREIGN KEY (query_by_valueset_id) REFERENCES query_to_valueset(id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

-- Create indexes for all primary and foreign keys

CREATE INDEX IF NOT EXISTS conditions_id_index ON conditions (id);
CREATE INDEX IF NOT EXISTS conditions_name_index ON conditions (name);

CREATE INDEX IF NOT EXISTS valuesets_id_index ON valuesets (id);

CREATE INDEX IF NOT EXISTS concepts_id_index ON concepts (id);

CREATE INDEX IF NOT EXISTS condition_to_valueset_id_index ON condition_to_valueset (id);
CREATE INDEX IF NOT EXISTS condition_to_valueset_condition_id_index ON condition_to_valueset (condition_id);
CREATE INDEX IF NOT EXISTS condition_to_valueset_valueset_id_index ON condition_to_valueset (valueset_id);

CREATE INDEX IF NOT EXISTS valueset_to_concept_id_index ON valueset_to_concept (id);
CREATE INDEX IF NOT EXISTS valueset_to_concept_valueset_id_index ON valueset_to_concept (valueset_id);
CREATE INDEX IF NOT EXISTS valueset_to_concept_concept_id_index ON valueset_to_concept (concept_id);

CREATE INDEX IF NOT EXISTS icd_crosswalk_id_index ON icd_crosswalk (id);

CREATE INDEX IF NOT EXISTS query_id_index ON query (id);
CREATE INDEX IF NOT EXISTS query_name_index ON query (query_name);

CREATE INDEX IF NOT EXISTS query_to_valueset_id_index ON query_to_valueset (id);
CREATE INDEX IF NOT EXISTS query_to_valueset_query_id_index ON query_to_valueset (query_id);
CREATE INDEX IF NOT EXISTS query_to_valueset_valueset_id_index ON query_to_valueset (valueset_id);

CREATE INDEX IF NOT EXISTS query_included_concepts_id_index ON query_included_concepts (id);
CREATE INDEX IF NOT EXISTS query_included_concepts_query_by_valueset_id_index ON query_included_concepts (query_by_valueset_id);
CREATE INDEX IF NOT EXISTS query_included_concepts_concept_id_index ON query_included_concepts (concept_id);
