import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";

export async function POST(request: NextRequest) {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  try {
    const requestBody = await request.json();
    // console.log("RB IS ", requestBody)

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

        return NextResponse.json(
          { message: "Success. Saved FHIR Bundle to database: " + saveECR },
          { status: 200 },
        );
      } catch (error) {
        console.error("Error inserting data to database:", error);
        return NextResponse.json(
          { message: "Failed to insert data to database." + error.message },
          { status: 400 },
        );
      }
    } else {
      return NextResponse.json(
        {
          error:
            "Invalid request body. Body must include a FHIR bundle with an ID.",
        },
        { status: 400 },
      );
    }
  } catch (error) {
    console.error("Error reading request body:", error);
    return NextResponse.json(
      { error: "Error reading request body. " + error.message },
      { status: 400 },
    );
  }
}
