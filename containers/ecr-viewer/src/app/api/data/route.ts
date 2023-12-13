import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";
export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams
  const ecr_id = params.get("id") ? params.get("id") : null;
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);
  
  const {ParameterizedQuery: PQ} = pgPromise;
  const findFhir = new PQ({text: 'SELECT * FROM fhir WHERE ecr_id = $1', values: [ecr_id]});
  try {
    const entry = await database.one(findFhir);
    return NextResponse.json({ fhirBundle: entry.data }, { status: 200 });
  } catch (error: any) {
    console.error('Error fetching data:', error);
    return NextResponse.json({ message: error.message }, { status: 500 });
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