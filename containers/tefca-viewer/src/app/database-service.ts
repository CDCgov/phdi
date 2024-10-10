"use server";
import { Pool, PoolConfig, QueryResultRow } from "pg";
import { Bundle, OperationOutcome } from "fhir/r4";
import { ValueSetItem, valueSetTypeToClincalServiceTypeMap } from "./constants";

const getQuerybyNameSQL = `
select q.query_name, q.id, qtv.valueset_id, vs.name as valueset_name, vs.author as author, vs.type, qic.concept_id, qic.include, c.code, c.code_system, c.display 
  from query q 
  left join query_to_valueset qtv on q.id = qtv.query_id 
  left join valuesets vs on qtv.valueset_id = vs.id
  left join query_included_concepts qic on qtv.id = qic.query_by_valueset_id 
  left join concepts c on qic.concept_id = c.id 
  where q.query_name = $1;
`;

// Load environment variables from .env and establish a Pool configuration
const dbConfig: PoolConfig = {
  connectionString: process.env.DATABASE_URL,
  max: 10, // Maximum # of connections in the pool
  idleTimeoutMillis: 30000, // A client must sit idle this long before being released
  connectionTimeoutMillis: 2000, // Wait this long before timing out when connecting new client
};
const dbClient = new Pool(dbConfig);

/**
 * Executes a search for a CustomQuery against the query-loaded Postgres
 * Database, using the saved name associated with the query as the unique
 * identifier by which to load the result.
 * @param name The name given to a stored query in the DB.
 * @returns One or more rows from the DB matching the requested saved query,
 * or an error if no results can be found.
 */
export const getSavedQueryByName = async (name: string) => {
  const values = [name];

  try {
    const result = await dbClient.query(getQuerybyNameSQL, values);
    if (result.rows.length === 0) {
      console.error("No results found for query:", name);
      return [];
    }
    return result.rows;
  } catch (error) {
    console.error("Error retrieving query:", error);
    throw error;
  }
};

/**
 * Helper function to filter the valueset-mapped rows of results returned from
 * the DB for particular types of related clinical services.
 * @param vsItems A list of value sets mapped from DB rows.
 * @param type One of "labs", "medications", or "conditions".
 * @returns A list of rows containing only the predicate service type.
 */
export const filterValueSets = async (
  vsItems: ValueSetItem[],
  type: "labs" | "medications" | "conditions",
) => {
  // Assign clinical code type based on desired filter
  // Mapping is established in TCR, so follow that convention
  let valuesetFilters = valueSetTypeToClincalServiceTypeMap[type];
  const results = vsItems.filter((vs) =>
    valuesetFilters.includes(vs.clinicalServiceType),
  );
  return results;
};

/**
 * Helper function that transforms and groups a set of database rows into a list of
 * ValueSet items grouped by author and code_system for display on the CustomizeQuery page.
 * @param rows The rows returned from the DB.
 * @returns A list of ValueSetItems grouped by author and system.
 */
export const mapQueryRowsToValueSetItems = async (rows: QueryResultRow[]) => {
  const vsItems = rows.map((r) => {
    const vsTranslation: ValueSetItem = {
      code: r["code"],
      display: r["display"],
      system: r["code_system"],
      include: r["include"],
      author: r["author"],
      valueSetName: r["valueset_name"],
      clinicalServiceType: r["type"],
    };
    return vsTranslation;
  });
  return vsItems;
};

/*
 * The expected return type from the eRSD API.
 */
type ErsdResponse = Bundle | OperationOutcome;

/**
 * Fetches the eRSD Specification from the eRSD API. This function requires an API key
 * to access the eRSD API. The API key can be obtained at https://ersd.aimsplatform.org/#/api-keys.
 * @param eRSDVersion - The version of the eRSD specification to retrieve. Defaults to v2.
 * @returns The eRSD Specification as a FHIR Bundle or an OperationOutcome if an error occurs.
 */
export async function getERSD(eRSDVersion: number = 2): Promise<ErsdResponse> {
  const ERSD_API_KEY = process.env.ERSD_API_KEY;
  const eRSDUrl = `https://ersd.aimsplatform.org/api/ersd/v${eRSDVersion}specification?format=json&api-key=${ERSD_API_KEY}`;
  const response = await fetch(eRSDUrl);
  if (response.status === 200) {
    const data = (await response.json()) as Bundle;
    return data;
  } else {
    return {
      resourceType: "OperationOutcome",
      issue: [
        {
          severity: "error",
          code: "processing",
          diagnostics: `Failed to retrieve data from eRSD: ${response.status} ${response.statusText}`,
        },
      ],
    } as OperationOutcome;
  }
}
