import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";

export async function POST(request: NextRequest) {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  console.log("DB", db);
  const database = db(db_url);

  try {
    const requestBody = await request.json();

    const fhirBundle = requestBody.fhirBundle;
    const ecrId = requestBody.fhirBundle.entry[0].resource.id;

    if (fhirBundle && ecrId) {
      const { ParameterizedQuery: PQ } = pgPromise;
      const addFhir = new PQ({
        text: "INSERT INTO fhir VALUES ($1, $2) RETURNING ecr_id",
        values: [ecrId, fhirBundle],
      });

      try {
        const saveECR = await database.one(addFhir);
        console.log("Created Resource with: ", saveECR);

        return new NextResponse(
          JSON.stringify({
            message:
              "Success. Saved FHIR Bundle to database: " + saveECR.ecr_id,
          }),
          { status: 200, headers: { "content-type": "application/json" } },
        );
      } catch (error) {
        console.error("Error inserting data to database:", error);
        return new NextResponse(
          JSON.stringify({
            message: "Failed to insert data to database." + error.message,
          }),
          { status: 400, headers: { "content-type": "application/json" } },
        );
      }
    } else {
      return new NextResponse(
        JSON.stringify({
          message:
            "Invalid request body. Body must include a FHIR bundle with an ID.",
        }),
        { status: 400, headers: { "content-type": "application/json" } },
      );
    }
  } catch (error) {
    console.error("Error reading request body:", error);
    return new NextResponse(
      JSON.stringify({ error: "Error reading request body. " + error.message }),
      { status: 400, headers: { "content-type": "application/json" } },
    );
  }
}
