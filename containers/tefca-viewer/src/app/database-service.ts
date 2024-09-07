"use server";
import { Pool, PoolConfig } from "pg";
import dotenv from "dotenv";

const getQuerybyNameSQL = `select q.query_name, q.id, qtv.valueset_id, qic.concept_id, qic.include, c.code, c.code_system, c.display 
      from query q 
      join query_to_valueset qtv on q.id = qtv.query_id 
      join query_included_concepts qic on qtv.id = qic.query_by_valueset_id 
      join concepts c on qic.concept_id = c.id 
      where q.query_name = $1;`;

// Load environment variables from tefca.env and establish a Pool configuration
dotenv.config({ path: "tefca.env" });
const dbConfig: PoolConfig = {
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  // port: Number(process.env.POSTGRES_PORT),
  connectionString: process.env.DATABASE_URL,
  database: process.env.POSTGRES_DB,
  max: 10, // Maximum # of connections in the pool
  idleTimeoutMillis: 30000, // A client must sit idle this long before being released
  connectionTimeoutMillis: 2000, // Wait this long before timing out when connecting new client
};

console.log("db service loaded", dbConfig);
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
    console.log("getSavedQueryByName", "name", name, "result", result.rows);
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
