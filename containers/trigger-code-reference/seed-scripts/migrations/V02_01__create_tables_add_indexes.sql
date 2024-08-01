-- create tables to link conditions to clinical services
CREATE TABLE IF NOT EXISTS valueset_types (
    id TEXT PRIMARY KEY,
    type TEXT
);

CREATE TABLE IF NOT EXISTS valuesets (
    id TEXT PRIMARY KEY,
    oid TEXT,
    version TEXT,
    name TEXT,
    author TEXT,
    type_id TEXT,
    FOREIGN KEY (type_id) REFERENCES valueset_types(id)
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
    version TEXT
);

CREATE TABLE IF NOT EXISTS condition_to_valueset (
    id TEXT PRIMARY KEY,
    condition_id TEXT,
    valueset_id TEXT,
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

CREATE TABLE IF NOT EXISTS condition_to_valueset_source (
    id TEXT PRIMARY KEY,
    map_id TEXT,
    source_id TEXT
);

CREATE TABLE IF NOT EXISTS terminology_sources (
    id TEXT PRIMARY KEY,
    name TEXT
);

-- add indexes to increase performance
-- conditions
CREATE INDEX IF NOT EXISTS "idx_conditions_id" ON conditions(id);

-- valuesets
CREATE INDEX IF NOT EXISTS "idx_valuesets_id" ON valuesets(id);
CREATE INDEX IF NOT EXISTS "idx_valuesets_type_id" ON valuesets(type_id);

-- valueset_types
CREATE INDEX IF NOT EXISTS "idx_valueset_types_id" ON valueset_types(id);

-- concepts
CREATE INDEX IF NOT EXISTS "idx_concepts_id" ON concepts(id);

-- valueset_to_concept indexes
CREATE INDEX IF NOT EXISTS "idx_valueset_to_concept_valueset_id" ON valueset_to_concept(valueset_id);
CREATE INDEX IF NOT EXISTS "idx_valueset_to_concept_concept_id" ON valueset_to_concept(concept_id);

-- condition_to_valueset indexes
CREATE INDEX IF NOT EXISTS "idx_condition_to_valueset_condition_id" ON condition_to_valueset(condition_id);
CREATE INDEX IF NOT EXISTS "idx_condition_to_valueset_valueset_id" ON condition_to_valueset(valueset_id);
