import { BlobServiceClient } from "@azure/storage-blob";
import { NextResponse } from "next/server";
import pgPromise from "pg-promise";
import {
  S3Client,
  PutObjectCommand,
  PutObjectCommandOutput,
} from "@aws-sdk/client-s3";
import { Bundle } from "fhir/r4";
import { S3_SOURCE, AZURE_SOURCE, POSTGRES_SOURCE } from "@/app/api/utils";

const s3Client =
  process.env.APP_ENV === "dev"
    ? new S3Client({
        region: process.env.AWS_REGION,
        endpoint: process.env.AWS_CUSTOM_ENDPOINT,
        forcePathStyle: process.env.AWS_CUSTOM_ENDPOINT !== undefined,
      })
    : new S3Client({ region: process.env.AWS_REGION });

/**
 * Saves a FHIR bundle to a postgres database.
 * @async
 * @function saveToPostgres
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle is successfully saved to postgres.
 * @throws {Error} Throws an error if the FHIR bundle cannot be saved to postgress.
 */
export const saveToPostgres = async (fhirBundle: Bundle, ecrId: string) => {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  const { ParameterizedQuery: PQ } = pgPromise;
  const addFhir = new PQ({
    text: "INSERT INTO fhir VALUES ($1, $2) RETURNING ecr_id",
    values: [ecrId, fhirBundle],
  });

  try {
    const saveECR = await database.one(addFhir);

    return NextResponse.json(
      { message: "Success. Saved FHIR Bundle to database: " + saveECR.ecr_id },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error inserting data to database:", error);
    return NextResponse.json(
      { message: "Failed to insert data to database. " + error.message },
      { status: 500 },
    );
  }
};

/**
 * Saves a FHIR bundle to an AWS S3 bucket.
 * @async
 * @function saveToS3
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle is successfully saved to the S3 bucket.
 * @throws {Error} Throws an error if the FHIR bundle cannot be saved to the S3 bucket.
 */
export const saveToS3 = async (fhirBundle: Bundle, ecrId: string) => {
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
    return NextResponse.json(
      { message: "Success. Saved FHIR Bundle to S3: " + ecrId },
      { status: 200 },
    );
  } catch (error: any) {
    console.error(error);
    return NextResponse.json(
      { message: "Failed to insert data to S3. " + error.message },
      { status: 500 },
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

    return NextResponse.json(
      { message: "Success. Saved FHIR bundle to Azure Blob Storage: " + ecrId },
      { status: 200 },
    );
  } catch (error: any) {
    return NextResponse.json(
      {
        message:
          "Failed to insert FHIR bundle to Azure Blob Storage. " +
          error.message,
      },
      { status: 500 },
    );
  }
};

interface BundleMetadata {
  last_name: string;
  first_name: string;
  birth_date: string;
  data_source: string;
  reportable_condition: string;
  rule_summary: string;
  report_date: string;
}

/**
 * @async
 * @function saveFhirData
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @param saveSource - The location to save the FHIR bundle. Valid values are "postgres", "s3", or "azure".
 * @returns A `NextResponse` object with a JSON payload indicating the success message. The response content type is set to `application/json`.
 */
export const saveFhirData = async (
  fhirBundle: Bundle,
  ecrId: string,
  saveSource: string,
) => {
  if (saveSource === S3_SOURCE) {
    return saveToS3(fhirBundle, ecrId);
  } else if (saveSource === AZURE_SOURCE) {
    return saveToAzure(fhirBundle, ecrId);
  } else if (saveSource === POSTGRES_SOURCE) {
    return await saveToPostgres(fhirBundle, ecrId);
  } else {
    return NextResponse.json(
      {
        message:
          'Invalid save source. Please provide a valid value for \'saveSource\' ("postgres", "s3", or "azure").',
      },
      { status: 400 },
    );
  }
};

/**
 * Saves a FHIR bundle metadata to a postgres database.
 * @async
 * @function saveToMetadataPostgres
 * @param metadata - The FHIR bundle metadata to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle metadata is successfully saved to postgres.
 * @throws {Error} Throws an error if the FHIR bundle metadata cannot be saved to postgress.
 */
export const saveToMetadataPostgres = async (
  metadata: BundleMetadata,
  ecrId: string,
) => {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  const { ParameterizedQuery: PQ } = pgPromise;
  const addMetadata = new PQ({
    text: "INSERT INTO fhir_metadata (ecr_id,patient_name_last,patient_name_first,patient_birth_date,data_source,reportable_condition,rule_summary,report_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING ecr_id",
    values: [
      ecrId,
      metadata.first_name,
      metadata.last_name,
      metadata.birth_date,
      "DB",
      metadata.reportable_condition,
      metadata.rule_summary,
      metadata.report_date,
    ],
  });

  try {
    const saveECR = await database.one(addMetadata);

    return NextResponse.json(
      { message: "Success. Saved metadata to database: " + saveECR.ecr_id },
      { status: 200 },
    );
  } catch (error: any) {
    console.error("Error inserting metadata to database:", error);
    return NextResponse.json(
      { message: "Failed to insert metadata to database. " + error.message },
      { status: 500 },
    );
  }
};

/**
 * @async
 * @function saveWithMetadata
 * @param fhirBundle - The FHIR bundle to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @param saveSource - The location to save the FHIR bundle. Valid values are "postgres", "s3", or "azure".
 * @param metadata - The metadata to be saved with the FHIR bundle.
 * @returns A `NextResponse` object with a JSON payload indicating the success message. The response content type is set to `application/json`.
 * @throws {Error} Throws an error if the FHIR bundle or metadata cannot be saved.
 */
export const saveWithMetadata = async (
  fhirBundle: Bundle,
  ecrId: string,
  saveSource: string,
  metadata: BundleMetadata,
) => {
  let fhirDataResult;
  let metadataResult;
  try {
    fhirDataResult = await saveFhirData(fhirBundle, ecrId, saveSource);
    metadataResult = await saveToMetadataPostgres(metadata, ecrId);
  } catch (error: any) {
    return NextResponse.json(
      { message: "Failed to save FHIR data with metadata. " + error.message },
      { status: 500 },
    );
  }

  let responseMessage = "";
  let responseStatus = 200;
  if (fhirDataResult.status !== 200) {
    responseMessage += "Failed to save FHIR data.\n";
    responseStatus = 500;
  } else {
    responseMessage += "Saved FHIR data.\n";
  }
  if (metadataResult.status !== 200) {
    responseMessage += "Failed to save metadata.";
    responseStatus = 500;
  } else {
    responseMessage += "Saved metadata.";
  }

  return NextResponse.json(
    { message: responseMessage },
    { status: responseStatus },
  );
};
