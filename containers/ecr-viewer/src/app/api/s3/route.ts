import { NextRequest, NextResponse } from "next/server";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { loadYamlConfig, streamToJson } from "../utils";

// Initialize the S3 client outside of your API route handler to reuse the connection
const s3Client = new S3Client({ region: process.env.AWS_REGION });

export async function GET(request: NextRequest) {
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
}
