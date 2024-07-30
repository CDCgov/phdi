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

CREATE TABLE IF NOT EXISTS condition_valueset_junction (
    id TEXT PRIMARY KEY,
    condition_id TEXT,
    valueset_id TEXT,
    FOREIGN KEY (condition_id) REFERENCES conditions(id),
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id)
);

CREATE TABLE IF NOT EXISTS valueset_concept_junction (
    id TEXT PRIMARY KEY,
    valueset_id TEXT,
    concept_id TEXT,
    FOREIGN KEY (valueset_id) REFERENCES valuesets(id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
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

-- valueset_concept_junction indexes
CREATE INDEX IF NOT EXISTS "idx_valueset_concept_junction_valueset_id" ON valueset_concept_junction(valueset_id);
CREATE INDEX IF NOT EXISTS "idx_valueset_concept_junction_concept_id" ON valueset_concept_junction(concept_id);

-- condition_valueset_junction indexes
CREATE INDEX IF NOT EXISTS "idx_condition_valueset_junction_condition_id" ON condition_valueset_junction(condition_id);
CREATE INDEX IF NOT EXISTS "idx_condition_valueset_junction_valueset_id" ON condition_valueset_junction(valueset_id);
