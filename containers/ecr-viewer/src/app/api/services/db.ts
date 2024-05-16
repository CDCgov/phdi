import pgp from "pg-promise";

const db_url = process.env.DATABASE_URL || "";
export const database = pgp()(db_url);
