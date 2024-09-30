import dotenv from "dotenv";

dotenv.config();
dotenv.config({ path: ".env.local", override: true });

console.log(process.env.SOURCE);
