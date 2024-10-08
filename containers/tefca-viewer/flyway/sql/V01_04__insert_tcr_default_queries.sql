-- Select data from the TCR that will be used to create default queries
WITH tcr_data AS (
    SELECT
        conditions.id AS condition_id,
        conditions.name AS condition_name,
        condition_to_valueset.valueset_id AS valueset_id,
        valuesets.oid as valueset_oid
    FROM conditions
    JOIN condition_to_valueset
        ON conditions.id = condition_to_valueset.condition_id
    join valuesets
    	on condition_to_valueset.valueset_id = valuesets.id
), 
-- Insert data into the query table
inserted_queries AS (
    INSERT INTO query (id, query_name, author, date_created, date_last_modified, time_window_number, time_window_unit)
    SELECT 
        uuid_generate_v4() AS id,
        condition_name AS query_name,
        'DIBBs' AS author,
        NOW() AS date_created,
        NOW() AS date_last_modified,
        1 AS time_window_number,
        'day' AS time_window_unit
    FROM tcr_data
    GROUP BY condition_name
    RETURNING id, query_name
),
-- Join the inserted_queries and tcr_data tables to create data for the query_to_valueset table
joined_data_for_qtv AS( 
	select
		inserted_queries.id as query_id,
		tcr_data.valueset_id as valueset_id,
		tcr_data.valueset_oid as valueset_oid
	from inserted_queries
	join tcr_data on inserted_queries.query_name = tcr_data.condition_name
),
-- Insert data into the query_to_valueset table
qic_data AS(
insert into query_to_valueset (id, query_id, valueset_id, valueset_oid)
select
	uuid_generate_v4() AS id,
	query_id,
	valueset_id,
	valueset_oid
from joined_data_for_qtv
returning id, valueset_id
)
-- Insert data into the query_included_concepts table
insert into query_included_concepts (id, query_by_valueset_id, concept_id, include)
select
	uuid_generate_v4() AS id,
	qic_data.id as query_by_valueset_id,
	vtc.concept_id as concept_id,
	TRUE
from qic_data
join valueset_to_concept vtc 
on qic_data.valueset_id = vtc.valueset_id;
