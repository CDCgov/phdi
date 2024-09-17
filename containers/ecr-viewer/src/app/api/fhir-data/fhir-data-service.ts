import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import {
  BlobClient,
  BlobDownloadResponseParsed,
  BlobServiceClient,
} from "@azure/storage-blob";
import { loadYamlConfig, streamToJson } from "../utils";
import { database } from "@/app/api/fhir-data/db";

const s3Client =
  process.env.APP_ENV === "dev"
    ? new S3Client({
        region: process.env.AWS_REGION,
        endpoint: process.env.AWS_CUSTOM_ENDPOINT,
        forcePathStyle: process.env.AWS_CUSTOM_ENDPOINT !== undefined,
      })
    : new S3Client({ region: process.env.AWS_REGION });

/**
 * Retrieves FHIR data from PostgreSQL database based on eCR ID.
 * @param request - The NextRequest object containing the request information.
 * @returns A promise resolving to a NextResponse object.
 */
export const get_postgres = async (request: NextRequest) => {
  const params = request.nextUrl.searchParams;
  const ecr_id = params.get("id") ? params.get("id") : null;
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
    if (error.message == "No data returned from the query.") {
      return NextResponse.json(
        { message: "eCR ID not found" },
        { status: 404 },
      );
    } else {
      return NextResponse.json({ message: error.message }, { status: 500 });
    }
  }
};

/**
 * Retrieves FHIR data from S3 based on eCR ID.
 * @param request - The NextRequest object containing the request information.
 * @returns A promise resolving to a NextResponse object.
 */
export const get_s3 = async (request: NextRequest) => {
  const params = request.nextUrl.searchParams;
  const ecr_id = params.get("id");
  const bucketName = process.env.ECR_BUCKET_NAME;
  const objectKey = `${ecr_id}.json`; // This could also come from the request, e.g., req.query.key

  try {
    const command = new GetObjectCommand({
      Bucket: bucketName,
      Key: objectKey,
    });

    const { Body } = await s3Client.send(command);
    const content = await streamToJson(Body);

    return NextResponse.json(
      { fhirBundle: content, fhirPathMappings: loadYamlConfig() },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("S3 GetObject error:", error);
    return NextResponse.json({ message: error.message }, { status: 500 });
  }
};

/**
 * Retrieves FHIR data from Azure Blob Storage based on eCR ID.
 * @param request - The NextRequest object containing the request information.
 * @returns A promise resolving to a NextResponse object.
 */
export const get_azure = async (request: NextRequest) => {
  // TODO: Make this global after we get Azure access
  const blobClient = BlobServiceClient.fromConnectionString(
    process.env.AZURE_STORAGE_CONNECTION_STRING!,
  );

  const params = request.nextUrl.searchParams;
  const ecr_id = params.get("id");

  if (!process.env.AZURE_CONTAINER_NAME)
    throw Error("Azure container name not found");

  const containerName = process.env.AZURE_CONTAINER_NAME;
  const blobName = `${ecr_id}.json`;

  try {
    const containerClient = blobClient.getContainerClient(containerName);
    const blockBlobClient: BlobClient = containerClient.getBlobClient(blobName);

    const downloadResponse: BlobDownloadResponseParsed =
      await blockBlobClient.download();
    const content = await streamToJson(downloadResponse.readableStreamBody);

    return NextResponse.json(
      { fhirBundle: content, fhirPathMappings: loadYamlConfig() },
      { status: 200 },
    );
  } catch (error: any) {
    console.error(
      "Failed to download the FHIR data from Azure Blob Storage:",
      error,
    );
    return NextResponse.json({ message: error.message }, { status: 500 });
  }
};
