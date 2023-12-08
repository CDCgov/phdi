import { NextRequest, NextResponse } from "next/server";
import fs from "fs"
import { searchObject } from "./utils";
import pgPromise from "pg-promise";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams
  const ecr_id = params.get("id") ? params.get("id") : null;
  console.log(ecr_id)
  const db = require('pg-promise')();
  console.log("DATABASE_URL: ", process.env.DATABASE_URL)
  const database = db(process.env.DATABASE_URL);
  
  const {ParameterizedQuery: PQ} = require('pg-promise');
  const findFhir = new PQ({text: 'SELECT * FROM fhir WHERE ecr_id = $1', values: [ecr_id]});
  try {
    const data = await database.one(findFhir);
    return NextResponse.json({ data: data, resourceType: "Bundle" }, { status: 200 });
  } catch (error) {
    console.error('Error fetching data:', error);
    return NextResponse.json({ error: error }, { status: 500 });
  }
  
}

export const getStaticProps = async () => {
  // Fetch data during build time
  const db = require('pg-promise')();
  const database = db(process.env.DATABASE_URL);
  const data = await database.one('SELECT * FROM your_table LIMIT 1');

  return {
    props: { data },
  };
};