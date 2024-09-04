import { BlobServiceClient } from "@azure/storage-blob";
import { NextResponse } from "next/server";
import pgPromise from "pg-promise";
import {
  S3Client,
  PutObjectCommand,
  PutObjectCommandOutput,
} from "@aws-sdk/client-s3";
import { Bundle } from "fhir/r4";

const s3Client = new S3Client({ region: process.env.AWS_REGION });

interface BundleMetaData {
  patient_name_last: string;
  patient_name_first: string;
  patient_birth_date: string;
  data_source: string;
  reportable_condition: string;
  rule_summary: string;
  report_date: string;
}

/**
 * Saves a FHIR bundle to a postgres database.
 * @async
 * @function saveToS3
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param bundleMetaData - The metadata associated with the FHIR bundle.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle is successfully saved to postgres.
 * @throws {Error} Throws an error if the FHIR bundle cannot be saved to postgress.
 */
export const saveToPostgres = async (
  fhirBundle: Bundle,
  bundleMetaData: BundleMetaData,
  ecrId: string,
) => {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  const { ParameterizedQuery: PQ } = pgPromise;
  const addFhir = new PQ({
    text: "INSERT INTO fhir VALUES ($1, $2) RETURNING ecr_id",
    values: [ecrId, fhirBundle],
  });

  try {
    await database.one(addFhir);
  } catch (error: any) {
    console.error("Error inserting data to database:", error);
    return NextResponse.json(
      { message: "Failed to insert data to database. " + error.message },
      { status: 400 },
    );
  }

  if (bundleMetaData) {
    const addMetaData = new PQ({
      text: "INSERT INTO fhir_metadata (ecr_id,patient_name_last,patient_name_first,patient_birth_date,data_source,reportable_condition,rule_summary,report_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
      values: [
        ecrId,
        bundleMetaData.patient_name_first,
        bundleMetaData.patient_name_last,
        bundleMetaData.patient_birth_date,
        bundleMetaData.data_source,
        bundleMetaData.reportable_condition,
        bundleMetaData.rule_summary,
        bundleMetaData.report_date,
      ],
    });

    try {
      await database.one(addMetaData);
      return NextResponse.json(
        {
          message:
            "Success. Saved FHIR bundle and metadata to database: " + ecrId,
        },
        { status: 200 },
      );
    } catch (error: any) {
      console.error("Error inserting metadata to database:", error);
      return NextResponse.json(
        {
          message:
            "Successfully inserted bundle to database but failed to insert data to database. " +
            error.message,
        },
        { status: 400 },
      );
    }
  }

  return NextResponse.json(
    {
      message: "Success. Saved FHIR bundle to database: " + ecrId,
    },
    { status: 200 },
  );
};

/**
 * Saves a FHIR bundle to an AWS S3 bucket.
 * @async
 * @function saveToS3
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param bundleMetadata - The metadata associated with the FHIR bundle.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle is successfully saved to the S3 bucket.
 * @throws {Error} Throws an error if the FHIR bundle cannot be saved to the S3 bucket.
 */
export const saveToS3 = async (
  fhirBundle: Bundle,
  bundleMetadata: BundleMetaData,
  ecrId: string,
) => {
  const bucketName = process.env.ECR_BUCKET_NAME;
  const objectKey = `${ecrId}.json`;
  const body = JSON.stringify(fhirBundle);

  try {
    const input = {
      Body: body,
      Bucket: bucketName,
      Key: objectKey,
      ContentType: "application/json",
    };

    const command = new PutObjectCommand(input);
    const response: PutObjectCommandOutput = await s3Client.send(command);
    const httpStatusCode = response?.$metadata?.httpStatusCode;

    if (httpStatusCode !== 200) {
      throw new Error(`HTTP Status Code: ${httpStatusCode}`);
    }
  } catch (error: any) {
    return NextResponse.json(
      { message: "Failed to insert data to S3. " + error.message },
      { status: 400 },
    );
  }

  if (bundleMetadata) {
    const metadataKey = `${ecrId}_metadata.json`;
    const metadataBody = JSON.stringify(bundleMetadata);

    try {
      const input = {
        Body: metadataBody,
        Bucket: bucketName,
        Key: metadataKey,
        ContentType: "application/json",
      };

      const command = new PutObjectCommand(input);
      const response: PutObjectCommandOutput = await s3Client.send(command);
      const httpStatusCode = response?.$metadata?.httpStatusCode;

      if (httpStatusCode !== 200) {
        throw new Error(`HTTP Status Code: ${httpStatusCode}`);
      }
    } catch (error: any) {
      return NextResponse.json(
        {
          message:
            "Successfully inserted bundle to S3 but failed to insert metadata to S3. " +
            error.message,
        },
        { status: 400 },
      );
    }

    return NextResponse.json(
      { message: "Success. Saved FHIR Bundle to S3: " + ecrId },
      { status: 200 },
    );
  }
};

/**
 * Saves a FHIR bundle to Azure Blob Storage.
 * @async
 * @function saveToAzure
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param ecrId - The unique ID for the eCR associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle is successfully saved to Azure Blob Storage.
 * @throws {Error} Throws an error if the FHIR bundle cannot be saved to Azure Blob Storage.
 */
export const saveToAzure = async (fhirBundle: Bundle, ecrId: string) => {
  // TODO: Make this global after we get Azure access
  const blobClient = BlobServiceClient.fromConnectionString(
    process.env.AZURE_STORAGE_CONNECTION_STRING!,
  );

  if (!process.env.AZURE_CONTAINER_NAME)
    throw Error("Azure container name not found");

  const containerName = process.env.AZURE_CONTAINER_NAME;
  const blobName = `${ecrId}.json`;
  const body = JSON.stringify(fhirBundle);

  try {
    const containerClient = blobClient.getContainerClient(containerName);
    const blockBlobClient = containerClient.getBlockBlobClient(blobName);

    const response = await blockBlobClient.upload(body, body.length, {
      blobHTTPHeaders: { blobContentType: "application/json" },
    });

    if (response._response.status !== 201) {
      throw new Error(`HTTP Status Code: ${response._response.status}`);
    }
  } catch (error: any) {
    return NextResponse.json(
      {
        message:
          "Failed to insert FHIR bundle to Azure Blob Storage. " +
          error.message,
      },
      { status: 400 },
    );
  }
};
