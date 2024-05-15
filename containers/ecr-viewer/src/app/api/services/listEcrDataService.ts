import { NextResponse } from "next/server";
import pgPromise from "pg-promise";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
import { database } from "@/app/api/services/db";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const s3Client = new S3Client({ region: process.env.AWS_REGION });

/**
 * Handles GET requests by fetching data from different sources based on the environment configuration.
 * It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
 * a supported source, it returns a JSON response indicating an invalid source.
 * @returns A promise that resolves to a `NextResponse` object
 *   if the source is invalid, or the result of fetching from the specified source.
 *   The specific return type (e.g., the type returned by `list_s3` or `list_postgres`)
 *   may vary based on the source and is thus marked as `unknown`.
 */
export async function listEcrData() {
  if (process.env.SOURCE === S3_SOURCE) {
    return list_s3();
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    return await list_postgres();
  } else {
    return NextResponse.json({ message: "Invalid source" }, { status: 500 });
  }
}

/**
 * Retrieves array of eCR IDs from PostgreSQL database.
 * @returns A promise resolving to a NextResponse object.
 */
export const list_postgres = async () => {
  const { ParameterizedQuery: PQ } = pgPromise;
  const listFhir = new PQ({
    text: "SELECT ecr_id FROM fhir",
  });
  try {
    const entry = await database.manyOrNone(listFhir);
    // TODO: changing this to not return a NextResponse? could just return entry
    return NextResponse.json(
      { data: entry, source: POSTGRES_SOURCE },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error fetching data:", error);
    if (error.message == "No data returned from the query.") {
      // TODO: throw error?
      return NextResponse.json({ message: "No eCRs found" }, { status: 404 });
    } else {
      return NextResponse.json({ message: error.message }, { status: 500 });
    }
  }
};

/**
 * Retrieves array of eCRs and their metadata from S3.
 * @returns A promise resolving to a NextResponse object.
 */
export const list_s3 = async () => {
  const bucketName = process.env.ECR_BUCKET_NAME;

  try {
    const command = new ListObjectsV2Command({
      Bucket: bucketName,
    });

    const response = await s3Client.send(command);

    return NextResponse.json(
      { data: response, source: S3_SOURCE },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("S3 GetObject error:", error);
    return NextResponse.json({ message: error.message }, { status: 500 });
  }
};
