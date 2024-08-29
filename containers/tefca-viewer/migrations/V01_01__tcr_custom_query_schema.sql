BEGIN;
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
    query_id UUID DEFAULT uuid_generate_v4 (),
    icd10_code TEXT,
    icd9_code TEXT,
    match_flags TEXT,
    PRIMARY KEY (query_id));

CREATE TABLE IF NOT EXISTS query_to_valueset (
    id TEXT PRIMARY KEY,
    query_id UUID,
    valueset_id TEXT,
    FOREIGN KEY (query_id) REFERENCES query(query_id),
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
COMMIT;