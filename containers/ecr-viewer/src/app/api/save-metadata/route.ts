import { NextRequest, NextResponse } from "next/server";
import { saveToPostgres } from "./save-metadata-service";

/**
 * Handles POST requests and saves the FHIR Bundle to the database.
 * @param request - The incoming request object. Expected to have a JSON body in the format `{"metadata":{}, ecrId}`.
 * @returns A `NextResponse` object with a JSON payload indicating the success message and the status code set to 200. The response content type is set to `application/json`.
 */
export async function POST(request: NextRequest) {
  let requestBody;
  let metadata;
  let ecrId;

  try {
    requestBody = await request.json();
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

  return await saveToPostgres(metadata, ecrId);
}
