CREATE TABLE ECR_DATA
(
    eICR_ID                  UNIQUEIDENTIFIER PRIMARY KEY,
    set_id                   VARCHAR(255),
    fhir_reference_link      VARCHAR(255),
    last_name                VARCHAR(255),
    first_name               VARCHAR(255),
    birth_date               DATE,
    gender                   VARCHAR(50),
    birth_sex                VARCHAR(50),
    gender_identity          VARCHAR(50),
    race                     VARCHAR(255),
    ethnicity                VARCHAR(255),
    street_address_1         VARCHAR(255),
    street_address_2         VARCHAR(255),
    state                    VARCHAR(50),
    zip_code                 VARCHAR(20),
    latitude                 FLOAT,
    longitude                FLOAT,
    homelessness_status      VARCHAR(255),
    disabilities             VARCHAR(255),
    tribal_affiliation       VARCHAR(255),
    tribal_enrollment_status VARCHAR(255),
    current_job_title        VARCHAR(255),
    current_job_industry     VARCHAR(255),
    usual_occupation         VARCHAR(255),
    usual_industry           VARCHAR(255),
    preferred_language       VARCHAR(255),
    pregnancy_status         VARCHAR(255),
    rr_id                    VARCHAR(255),
    processing_status        VARCHAR(255),
    eicr_version_number      VARCHAR(50),
    authoring_datetime       DATETIME,
    authoring_provider       VARCHAR(255),
    provider_id              VARCHAR(255),
    facility_id              VARCHAR(255),
    facility_name            VARCHAR(255),
    encounter_type           VARCHAR(255),
    encounter_start_date     DATETIME,
    encounter_end_date       DATETIME,
    reason_for_visit         VARCHAR(255),
    active_problems          VARCHAR(255)
);

CREATE TABLE ecr_rr_conditions
(
    UUID      UNIQUEIDENTIFIER PRIMARY KEY,
    eICR_ID   UNIQUEIDENTIFIER FOREIGN KEY REFERENCES ECR_DATA (eICR_ID),
    condition VARCHAR(255),
);

CREATE TABLE ecr_rr_rule_summaries
(
    UUID                 UNIQUEIDENTIFIER PRIMARY KEY,
    ECR_RR_CONDITIONS_ID UNIQUEIDENTIFIER FOREIGN KEY REFERENCES ecr_rr_conditions (UUID),
    rule_summary         VARCHAR(MAX)
);


CREATE TABLE ecr_labs
(
    UUID                                   UNIQUEIDENTIFIER PRIMARY KEY,
    eICR_ID                                UNIQUEIDENTIFIER FOREIGN KEY REFERENCES ECR_DATA (eICR_ID),
    test_type                              VARCHAR(255),
    test_type_code                         VARCHAR(50),
    test_type_system                       VARCHAR(50),
    test_result_qualitative                VARCHAR(255),
    test_result_quantitative               FLOAT,
    test_result_units                      VARCHAR(50),
    test_result_code                       VARCHAR(50),
    test_result_code_display               VARCHAR(255),
    test_result_code_system                VARCHAR(50),
    test_result_interpretation             VARCHAR(255),
    test_result_interpretation_code        VARCHAR(50),
    test_result_interpretation_system      VARCHAR(50),
    test_result_reference_range_low_value  FLOAT,
    test_result_reference_range_low_units  VARCHAR(50),
    test_result_reference_range_high_value FLOAT,
    test_result_reference_range_high_units VARCHAR(50),
    specimen_type                          VARCHAR(255),
    specimen_collection_date               DATE,
    performing_lab                         VARCHAR(255)
);
