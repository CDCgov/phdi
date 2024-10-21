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
import sql from "mssql";
import { randomUUID } from "crypto";
import { BundleExtendedMetadata, BundleMetadata } from "./types";

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
      {
        message: `Failed to insert data to database. ${error.message} url: ${db_url}`,
      },
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
 * @async
 * @function saveMetadataToSqlServer
 * @param metadata - The FHIR bundle metadata to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A `NextResponse` object with a JSON payload indicating the success message. The response content type is set to `application/json`.
 */
export const saveMetadataToSqlServer = async (
  metadata: BundleExtendedMetadata,
  ecrId: string,
) => {
  let pool = await sql.connect({
    user: process.env.SQL_SERVER_USER,
    password: process.env.SQL_SERVER_PASSWORD,
    server: process.env.SQL_SERVER_HOST || "localhost",
    options: {
      trustServerCertificate: true,
    },
  });

  if (process.env.METADATA_DATABASE_SCHEMA == "extended") {
    try {
      const transaction = new sql.Transaction(pool);
      await transaction.begin();
      const ecrDataInsertRequest = new sql.Request(transaction);
      await ecrDataInsertRequest
        .input("eICR_ID", sql.VarChar(200), metadata.eicr_id)
        .input("eicr_set_id", sql.VarChar(255), metadata.eicr_set_id)
        .input("last_name", sql.VarChar(255), metadata.last_name)
        .input("first_name", sql.VarChar(255), metadata.last_name)
        .input("birth_date", sql.Date, metadata.birth_date)
        .input("gender", sql.VarChar(50), metadata.gender)
        .input("birth_sex", sql.VarChar(50), metadata.birth_sex)
        .input("gender_identity", sql.VarChar(50), metadata.gender_identity)
        .input("race", sql.VarChar(255), metadata.race)
        .input("ethnicity", sql.VarChar(255), metadata.ethnicity)
        .input("street_address1", sql.VarChar(255), metadata.street_address1)
        .input("street_address2", sql.VarChar(255), metadata.street_address2)
        .input("state", sql.VarChar(50), metadata.state)
        .input("zip_code", sql.VarChar(50), metadata.zip)
        .input("latitude", sql.Float, metadata.latitude)
        .input("longitude", sql.Float, metadata.longitude)
        .input(
          "homelessness_status",
          sql.VarChar(255),
          metadata.homelessness_status,
        )
        .input("disabilities", sql.VarChar(255), metadata.disabilities)
        .input(
          "tribal_affiliation",
          sql.VarChar(255),
          metadata.tribal_affiliation,
        )
        .input(
          "tribal_enrollment_status",
          sql.VarChar(255),
          metadata.tribal_enrollment_status,
        )
        .input(
          "current_job_title",
          sql.VarChar(255),
          metadata.current_job_title,
        )
        .input(
          "current_job_industry",
          sql.VarChar(255),
          metadata.current_job_industry,
        )
        .input("usual_occupation", sql.VarChar(255), metadata.usual_occupation)
        .input("usual_industry", sql.VarChar(255), metadata.usual_industry)
        .input(
          "preferred_language",
          sql.VarChar(255),
          metadata.preferred_language,
        )
        .input("pregnancy_status", sql.VarChar(255), metadata.pregnancy_status)
        .input("rr_id", sql.VarChar(255), metadata.rr_id)
        .input(
          "processing_status",
          sql.VarChar(255),
          metadata.processing_status,
        )
        .input(
          "eicr_version_number",
          sql.VarChar(50),
          metadata.eicr_version_number,
        )
        .input("authoring_date", sql.Date, metadata.authoring_datetime)
        .input("authoring_time", sql.Time(7), metadata.authoring_datetime)
        .input("authoring_provider", sql.VarChar(255), metadata.provider_id)
        .input("provider_id", sql.VarChar(255), metadata.provider_id)
        .input("facility_id", sql.VarChar(255), metadata.facility_id_number)
        .input("facility_name", sql.VarChar(255), metadata.facility_name)
        .input("encounter_type", sql.VarChar(255), metadata.encounter_type)
        .input("encounter_start_date", sql.Date, metadata.encounter_start_date)
        .input(
          "encounter_start_time",
          sql.Time(7),
          metadata.encounter_start_date,
        )
        .input("encounter_end_date", sql.Date, metadata.encounter_end_date)
        .input("encounter_end_time", sql.Time(7), metadata.encounter_end_date)
        .input(
          "reason_for_visit",
          sql.VarChar(sql.MAX),
          metadata.reason_for_visit,
        )
        .input(
          "active_problems",
          sql.VarChar(sql.MAX),
          metadata.active_problems,
        )
        .query(
          "INSERT INTO dbo.ECR_DATA VALUES (@eICR_ID, @eicr_set_id, @fhir_reference_link, @last_name, @first_name, @birth_date, @gender, @birth_sex, @gender_identity, @race, @ethnicity, @street_address1, @street_address2, @state, @zip_code, @latitude, @longitude, @homelessness_status, @disabilities, @tribal_affiliation, @tribal_enrollment_status, @current_job_title, @current_job_industry, @usual_occupation, @usual_industry, @preferred_language, @pregnancy_status, @rr_id, @processing_status, @eicr_version_number, @authoring_date, @authoring_time, @authoring_provider, @provider_id, @facility_id, @facility_name, @encounter_type, @encounter_start_date, @encounter_start_time, @encounter_end_date, @encounter_end_time, @reason_for_visit, @active_problems)",
        );

      if (metadata.labs) {
        for (const lab of metadata.labs) {
          const labInsertRequest = new sql.Request(transaction);
          await labInsertRequest
            .input("UUID", sql.VarChar(200), lab.uuid)
            .input("eICR_ID", sql.VarChar(200), metadata.eicr_id)
            .input("test_type", sql.VarChar(200), lab.test_type)
            .input("test_type_code", sql.VarChar(50), lab.test_type_code)
            .input("test_type_system", sql.VarChar(50), lab.test_type_system)
            .input(
              "test_result_qualitative",
              sql.VarChar(255),
              lab.test_result_qualitative,
            )
            .input(
              "test_result_quantitative",
              sql.Float,
              lab.test_result_quantitative,
            )
            .input("test_result_units", sql.VarChar(50), lab.test_result_units)
            .input("test_result_code", sql.VarChar(50), lab.test_result_code)
            .input(
              "test_result_code_display",
              sql.VarChar(255),
              lab.test_result_code_display,
            )
            .input(
              "test_result_code_system",
              sql.VarChar(50),
              lab.test_result_code_system,
            )
            .input(
              "test_result_interpretation_system",
              sql.VarChar(255),
              lab.test_result_interp_system,
            )
            .input(
              "test_result_ref_range_low_value",
              sql.Float,
              lab.test_result_ref_range_low,
            )
            .input(
              "test_result_ref_range_low_units",
              sql.VarChar(50),
              lab.test_result_ref_range_low_units,
            )
            .input(
              "test_result_ref_range_high_value",
              sql.Float,
              lab.test_result_ref_range_high,
            )
            .input(
              "test_result_ref_range_high_units",
              sql.VarChar(50),
              lab.test_result_ref_range_high_units,
            )
            .input("specimen_type", sql.VarChar(255), lab.specimen_type)
            .input(
              "specimen_collection_date",
              sql.Date,
              lab.specimen_collection_date,
            )
            .input("performing_lab", sql.VarChar(255), lab.performing_lab)
            .query(
              "INSERT INTO dbo.ecr_labs VALUES (@UUID, @eICR_ID, @test_type, @test_type_code, @test_type_system, @test_result_qualitative, @test_result_quantitative, @test_result_units, @test_result_code, @test_result_code_display, @test_result_code_system, @test_result_interpretation, @test_result_interpretation_code, @test_result_interpretation_system, @test_result_ref_range_low_value, @test_result_ref_range_low_units, @test_result_ref_range_high_value, @test_result_ref_range_high_units, @specimen_type, @specimen_collection_date, @performing_lab)",
            );
        }
      }

      if (metadata.rr) {
        for (const rule of metadata.rr) {
          const rr_conditions_uuid = randomUUID();
          const rrConditionsInsertRequest = new sql.Request(transaction);
          rrConditionsInsertRequest
            .input("UUID", sql.VarChar(200), rr_conditions_uuid)
            .input("eICR_ID", sql.VarChar(200), metadata.eicr_id)
            .input("condition", sql.VarChar(sql.MAX), rule.condition)
            .query(
              "INSERT INTO dbo.ecr_rr_conditions VALUES (@UUID, @eICR_ID, @condition)",
            );

          const ruleSummaryInsertRequest = new sql.Request(transaction);
          await ruleSummaryInsertRequest
            .input("UUID", sql.VarChar(200), randomUUID())
            .input("ECR_RR_CONDITIONS_ID", sql.VarChar(200), rr_conditions_uuid)
            .input("rule_summary", sql.VarChar(sql.MAX), rule.rule_summaries)
            .query(
              "INSERT INTO dbo.ecr_rr_rule_summaries VALUES (@UUID, @ECR_RR_CONDITIONS_ID, @rule_summary)",
            );
        }
      }

      await transaction.commit();

      return NextResponse.json(
        { message: "Success. Saved metadata to database: " + ecrId },
        { status: 200 },
      );
    } catch (error: any) {
      console.error("Error inserting metadata to database:", error);

      if (pool) {
        const transaction = new sql.Transaction(pool);
        await transaction.rollback();
      }

      return NextResponse.json(
        { message: "Failed to insert metadata to database. " + error.message },
        { status: 500 },
      );
    }
  } else {
    return NextResponse.json(
      {
        message:
          "Only the extended metadata schema is implemented for SQL Server.",
      },
      { status: 501 },
    );
  }
};

/**
 * Saves a FHIR bundle metadata to a postgres database.
 * @async
 * @function saveMetadataToPostgres
 * @param metadata - The FHIR bundle metadata to be saved.
 * @param ecrId - The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.
 * @returns A promise that resolves when the FHIR bundle metadata is successfully saved to postgres.
 * @throws {Error} Throws an error if the FHIR bundle metadata cannot be saved to postgress.
 */
export const saveMetadataToPostgres = async (
  metadata: BundleMetadata,
  ecrId: string,
) => {
  const db_url = process.env.DATABASE_URL || "";
  const db = pgPromise();
  const database = db(db_url);

  const { ParameterizedQuery: PQ } = pgPromise;

  let addMetadata = undefined;
  if (process.env.METADATA_DATABASE_SCHEMA == "extended") {
    return NextResponse.json(
      {
        message:
          "Only the default metadata schema is implemented for Postgres.",
      },
      { status: 501 },
    );
  } else {
    addMetadata = new PQ({
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
  }

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
  metadata: BundleMetadata | BundleExtendedMetadata,
) => {
  let fhirDataResult;
  let metadataResult;
  const metadataSaveLocation = process.env.METADATA_DATABASE_TYPE;
  try {
    fhirDataResult = await saveFhirData(fhirBundle, ecrId, saveSource);

    if (metadataSaveLocation == "postgres") {
      metadataResult = await saveMetadataToPostgres(
        metadata as BundleMetadata,
        ecrId,
      );
    } else if (metadataSaveLocation == "sqlserver") {
      metadataResult = await saveMetadataToSqlServer(
        metadata as BundleExtendedMetadata,
        ecrId,
      );
    } else {
      metadataResult = NextResponse.json({
        message: "Unknown metadataSaveLocation: " + metadataSaveLocation,
      });
    }
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
    responseStatus = fhirDataResult.status;
  } else {
    responseMessage += "Saved FHIR data.\n";
  }
  if (metadataResult.status !== 200) {
    responseMessage += "Failed to save metadata.";
    responseStatus = metadataResult.status;
  } else {
    responseMessage += "Saved metadata.";
  }

  return NextResponse.json(
    { message: responseMessage },
    { status: responseStatus },
  );
};
