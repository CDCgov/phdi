import { NextResponse } from "next/server";
import pgPromise from "pg-promise";
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
import { database } from "@/app/api/fhir-data/db";

const s3Client = new S3Client({ region: process.env.AWS_REGION });
const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

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
    return NextResponse.json(
      { data: entry, source: POSTGRES_SOURCE },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error fetching data:", error);
    if (error.message == "No data returned from the query.") {
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
