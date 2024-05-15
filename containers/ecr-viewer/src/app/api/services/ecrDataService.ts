import pgPromise from "pg-promise";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { streamToJson } from "@/app/api/services/utils";
import { database } from "@/app/api/services/db";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const s3Client = new S3Client({ region: process.env.AWS_REGION });

/**
 * Get eCR data based on the ecrID.
 * @param ecrId - The id of the eCR.
 * @returns A promise resolving to eCR data.
 */
export const getEcrData = async (ecrId: string) => {
  if (process.env.SOURCE === S3_SOURCE) {
    return await getS3Data(ecrId);
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    return await getPostgresData(ecrId);
  }
};

/**
 * Retrieves FHIR data from Postgres based on eCR ID.
 * @param ecrId - The id of the ecr.
 * @returns A promise resolving to eCR data.
 */
const getPostgresData = async (ecrId: string) => {
  const { ParameterizedQuery: PQ } = pgPromise;
  const findFhir = new PQ({
    text: "SELECT * FROM fhir WHERE ecr_id = $1",
    values: [ecrId],
  });
  return (await database.one(findFhir)).data;
};

/**
 * Retrieves FHIR data from S3 based on eCR ID.
 * @param ecrId - The id of the ecr.
 * @returns A promise resolving to eCR data.
 */
const getS3Data = async (ecrId: string) => {
  const bucketName = process.env.ECR_BUCKET_NAME;
  const objectKey = `${ecrId}.json`; // This could also come from the request, e.g., req.query.key
  const command = new GetObjectCommand({
    Bucket: bucketName,
    Key: objectKey,
  });

  const { Body } = await s3Client.send(command);
  return await streamToJson(Body);
};
