import { Pool } from "pg";
import dotenv from "dotenv";

// Load environment variables from tefca.env
dotenv.config({ path: "tefca.env" });

const dbClient = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: Number(process.env.POSTGRES_PORT),
  max: 10, // Maximum # of connections in the pool
  idleTimeoutMillis: 30000, // Idle time before releasing a connection
  connectionTimeoutMillis: 2000, // Timeout for establishing a new connection
});

export default dbClient;

export const getQuerybyId = async (id: string) => {
  const query = "SELECT * FROM query WHERE id = $1";
  const values = [id];

  try {
    const result = await dbClient.query(query, values);
    return result.rows[0];
  } catch (error) {
    console.error("Error retrieving user:", error);
    throw error;
  }
};
