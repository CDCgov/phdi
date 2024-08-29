BEGIN;
CREATE TABLE conditions (
    id TEXT PRIMARY KEY,
    system TEXT,
    name TEXT,
    version TEXT
);

CREATE TABLE valuesets (
    id TEXT PRIMARY KEY,
    oid TEXT,
    version TEXT,
    name TEXT,
    author TEXT,
    type TEXT
);

CREATE TABLE concepts (
    id TEXT PRIMARY KEY,
    code TEXT,
    code_system TEXT,
    display TEXT,
    gem_formatted_code TEXT,
    version TEXT
);

CREATE TABLE condition_to_valueset (
    id TEXT PRIMARY KEY,
    condition_id TEXT,
    valueset_id TEXT,
    source TEXT,
    FOREIGN KEY (condition_id) REFERENCES conditions(id),
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id)
);

CREATE TABLE valueset_to_concept (
    id TEXT PRIMARY KEY,
    valueset_id TEXT,
    concept_id TEXT,
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

CREATE TABLE icd_crosswalk (
    id TEXT PRIMARY KEY,
    icd10_code TEXT,
    icd9_code TEXT,
    match_flags TEXT);

COMMIT;