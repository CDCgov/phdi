"use server";
import { Pool } from "pg";
import dotenv from "dotenv";

// Load environment variables from tefca.env
dotenv.config({ path: "tefca.env" });
console.log("db service loaded", {
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  port: Number(process.env.POSTGRES_PORT),
  database: process.env.POSTGRES_DB,
  max: 10, // Maximum # of connections in the pool
  idleTimeoutMillis: 30_000, // Idle time before releasing a connection
  connectionTimeoutMillis: 20_000, // Timeout for establishing a new connection
});
const dbClient = new Pool({
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  port: Number(process.env.POSTGRES_PORT),
  database: process.env.POSTGRES_DB,
  max: 10, // Maximum # of connections in the pool
  idleTimeoutMillis: 30_000, // Idle time before releasing a connection
  connectionTimeoutMillis: 20_000, // Timeout for establishing a new connection
});

export const getQuerybyName = async (name: string, query: string) => {
  const values = [name];

  try {
    const result = await dbClient.query(query, values);
    console.log("getQuerybyId", "name", name, "result", result.rows);
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
