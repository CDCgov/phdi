import { NextRequest, NextResponse } from "next/server";
import pgPromise from "pg-promise";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { loadYamlConfig, streamToJson } from "../utils";
import { database } from "@/app/api/fhir-data/db";

const s3Client = new S3Client({ region: process.env.AWS_REGION });

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
