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
