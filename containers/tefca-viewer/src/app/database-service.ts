"use server";
import { Pool, PoolConfig, QueryResultRow } from "pg";
import dotenv from "dotenv";
import { ValueSetItem } from "./constants";

const getQuerybyNameSQL = `
select q.query_name, q.id, q.author, qtv.valueset_id, vs.type, qic.concept_id, qic.include, c.code, c.code_system, c.display 
  from query q 
  left join query_to_valueset qtv on q.id = qtv.query_id 
  left join valuesets vs on qtv.valueset_id = vs.id
  left join query_included_concepts qic on qtv.id = qic.query_by_valueset_id 
  left join concepts c on qic.concept_id = c.id 
  where q.query_name = $1;
`;

// Load environment variables from tefca.env and establish a Pool configuration
dotenv.config({ path: "tefca.env" });
const dbConfig: PoolConfig = {
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  connectionString: process.env.DATABASE_URL,
  port: Number(process.env.POSTGRES_PORT),
  database: process.env.POSTGRES_DB,
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
 * Helper function to filter the rows of results returned from the DB for particular
 * types of related clinical services.
 * @param dbResults The list of results returned from the DB.
 * @param type One of "labs", "medications", or "conditions".
 * @returns A list of rows containing only the predicate service type.
 */
export const filterQueryRows = async (
  dbResults: QueryResultRow[],
  type: "labs" | "medications" | "conditions",
) => {
  // Assign clinical code type based on desired filter
  // Mapping is established in TCR, so follow that convention
  let valuesetFilters;
  if (type == "labs") {
    valuesetFilters = ["ostc", "lotc", "lrtc"];
  } else if (type == "medications") {
    valuesetFilters = ["mrtc"];
  } else {
    valuesetFilters = ["dxtc", "sdtc"];
  }
  const results = dbResults.filter((row) =>
    valuesetFilters.includes(row["type"]),
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
  // Group by author and code_system
  const grouped = rows.reduce(
    (acc, row) => {
      const groupKey = `${row.author}:${row.code_system}`;
      if (!acc[groupKey]) {
        acc[groupKey] = {
          author: row.author,
          system: row.code_system,
          items: [],
        };
      }
      acc[groupKey].items.push({
        code: row["code"],
        display: row["display"],
        system: row["code_system"],
        include: row["include"],
        author: row["author"],
      });
      return acc;
    },
    {} as Record<
      string,
      { author: string; system: string; items: ValueSetItem[] }
    >,
  );

  return Object.values(grouped);
};
