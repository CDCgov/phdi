import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";
import { loadYamlConfig } from "./utils";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const ecr_id = params.get("id") ? params.get("id") : null;
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);
  const mappings = loadYamlConfig();

  const { ParameterizedQuery: PQ } = pgPromise;
  const findFhir = new PQ({
    text: "SELECT * FROM fhir WHERE ecr_id = $1",
    values: [ecr_id],
  });
  try {
    if (!mappings) throw Error;
    const entry = await database.one(findFhir);
    return NextResponse.json(
      { fhirBundle: entry.data, fhirPathMappings: mappings },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error fetching data:", error);
    return NextResponse.json({ message: error.message }, { status: 500 });
  }
}
