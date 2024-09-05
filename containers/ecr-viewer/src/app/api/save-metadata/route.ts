import { NextRequest, NextResponse } from "next/server";
import { saveToAzure, saveToPostgres, saveToS3 } from "./save-metadata-service";
import { S3_SOURCE, AZURE_SOURCE, POSTGRES_SOURCE } from "@/app/api/utils";

/**
 * Handles POST requests and saves the FHIR Bundle to the database.
 * @param request - The incoming request object. Expected to have a JSON body in the format `{"fhirBundle":{}, "saveSource": "postgres|s3""}`. FHIR bundle must include the ecr ID under entry[0].resource.id.
 * @returns A `NextResponse` object with a JSON payload indicating the success message and the status code set to 200. The response content type is set to `application/json`.
 */
export async function POST(request: NextRequest) {
  let requestBody;
  let metadata;
  let saveSource;
  let ecrId;

  try {
    requestBody = await request.json();
    saveSource = requestBody.saveSource;
    ecrId = requestBody.ecr_id;
    metadata = requestBody.metadata;
  } catch (error: any) {
    console.error("Error reading request body:", error);
    return NextResponse.json(
      { message: "Error reading request body. " + error.message },
      { status: 400 },
    );
  }

  if (!metadata || !ecrId) {
    return NextResponse.json(
      {
        message:
          "Error reading request body. Body must include metadata with an ID.",
      },
      { status: 400 },
    );
  }

  if (!saveSource) {
    return NextResponse.json(
      {
        message:
          'Save location is undefined. Please provide a valid value for \'saveSource\' ("postgres", "s3", or "azure").',
      },
      { status: 400 },
    );
  }

  if (saveSource === S3_SOURCE) {
    return saveToS3(metadata, ecrId);
  } else if (saveSource === AZURE_SOURCE) {
    return saveToAzure(metadata, ecrId);
  } else if (saveSource === POSTGRES_SOURCE) {
    return await saveToPostgres(metadata, ecrId);
  } else {
    return NextResponse.json(
      {
        message:
          'Invalid save source. Please provide a valid value for \'saveSource\' ("postgres", "s3", or "azure").',
      },
      { status: 400 },
    );
  }
}
