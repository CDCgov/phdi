import { NextRequest, NextResponse } from "next/server";
import { saveFhirData, saveWithMetadata } from "./save-fhir-data-service";
import { S3_SOURCE, AZURE_SOURCE, POSTGRES_SOURCE } from "@/app/api/utils";

/**
 * Handles POST requests and saves the FHIR Bundle to the database.
 * @param request - The incoming request object. Expected to have a JSON body in the format `{"fhirBundle":{}, "saveSource": "postgres|s3|azure""}`. FHIR bundle must include the ecr ID under entry[0].resource.id.
 * @returns A `NextResponse` object with a JSON payload indicating the success message. The response content type is set to `application/json`.
 */
export async function POST(request: NextRequest) {
  let requestBody;
  let fhirBundle;
  let saveSource;
  let ecrId;

  try {
    requestBody = await request.json();
    fhirBundle = requestBody.fhirBundle;
    saveSource = requestBody.saveSource;
    ecrId = requestBody.fhirBundle.entry[0].resource.id;
  } catch (error: any) {
    console.error("Error reading request body:", error);
    return NextResponse.json(
      { message: "Error reading request body. " + error.message },
      { status: 400 },
    );
  }

  if (!fhirBundle || !ecrId) {
    return NextResponse.json(
      {
        message:
          "Error reading request body. Body must include a FHIR bundle with an ID.",
      },
      { status: 400 },
    );
  }

  if (!saveSource) {
    saveSource = process.env.SOURCE;
  }

  if (
    [S3_SOURCE, AZURE_SOURCE, POSTGRES_SOURCE].includes(saveSource) == false
  ) {
    return NextResponse.json({ message: "Invalid source" }, { status: 500 });
  }

  if (requestBody.metadata) {
    return saveWithMetadata(
      fhirBundle,
      ecrId,
      saveSource,
      requestBody.metadata,
    );
  } else {
    return saveFhirData(fhirBundle, ecrId, saveSource);
  }
}
