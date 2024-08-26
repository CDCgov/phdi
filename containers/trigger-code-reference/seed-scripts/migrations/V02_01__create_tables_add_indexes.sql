CREATE TABLE IF NOT EXISTS valuesets (
    id TEXT PRIMARY KEY,
    oid TEXT,
    version TEXT,
    name TEXT,
    author TEXT,
    type TEXT
);

CREATE TABLE IF NOT EXISTS conditions (
    id TEXT PRIMARY KEY,
    system TEXT,
    name TEXT,
    version TEXT
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
    match_flags TEXT,
    FOREIGN KEY (icd10_code) REFERENCES concepts(gem_formatted_code)
);


-- add indexes to increase performance
-- conditions
CREATE INDEX IF NOT EXISTS "idx_conditions_id" ON conditions(id);

-- valuesets
CREATE INDEX IF NOT EXISTS "idx_valuesets_id" ON valuesets(id);

-- concepts
CREATE INDEX IF NOT EXISTS "idx_concepts_id" ON concepts(id);

-- valueset_to_concept indexes
CREATE INDEX IF NOT EXISTS "idx_valueset_to_concept_valueset_id" ON valueset_to_concept(valueset_id);
CREATE INDEX IF NOT EXISTS "idx_valueset_to_concept_concept_id" ON valueset_to_concept(concept_id);

-- condition_to_valueset indexes
CREATE INDEX IF NOT EXISTS "idx_condition_to_valueset_condition_id" ON condition_to_valueset(condition_id);
CREATE INDEX IF NOT EXISTS "idx_condition_to_valueset_valueset_id" ON condition_to_valueset(valueset_id);
