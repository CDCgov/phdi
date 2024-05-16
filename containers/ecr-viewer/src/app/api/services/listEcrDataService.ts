import pgPromise from "pg-promise";
import {
  S3Client,
  ListObjectsV2Command,
  ListObjectsV2CommandOutput,
} from "@aws-sdk/client-s3";
import { database } from "@/app/api/services/db";
import { formatDateTime } from "@/app/services/formatService";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const s3Client = new S3Client({ region: process.env.AWS_REGION });

export type ListEcr = {
  ecrId: string;
  dateModified: string;
}[];

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
    const data = await list_s3();
    return processListS3(data);
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    const data = await list_postgres();
    return processListPostgres(data);
  } else {
    throw Error("Invalid Source");
  }
}

/**
 * Retrieves array of eCR IDs from PostgreSQL database.
 * @returns A promise resolving to a NextResponse object.
 */
const list_postgres = async () => {
  const { ParameterizedQuery: PQ } = pgPromise;
  const listFhir = new PQ({
    text: "SELECT ecr_id FROM fhir",
  });
  try {
    return await database.manyOrNone(listFhir);
  } catch (error: any) {
    console.error("Error fetching data:", error);
    if (error.message == "No data returned from the query.") {
      throw Error("No eCRs found");
    } else {
      throw Error(error.message);
    }
  }
};

/**
 * Retrieves array of eCRs and their metadata from S3.
 * @returns A promise resolving to a NextResponse object.
 */
const list_s3 = async () => {
  const bucketName = process.env.ECR_BUCKET_NAME;

  try {
    const command = new ListObjectsV2Command({
      Bucket: bucketName,
    });

    return await s3Client.send(command);
  } catch (error: any) {
    console.error("S3 GetObject error:", error);
    throw Error(error.message);
  }
};

/**
 * Processes a list of eCR data retrieved from Postgres.
 * @param responseBody - The response body containing eCR data from Postgres.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processListPostgres = (responseBody: any[]): ListEcr => {
  return responseBody.map((object) => {
    return {
      ecrId: object.ecr_id || "",
      dateModified: "N/A",
    };
  });
};

/**
 * Processes a list of eCR data retrieved from an S3 bucket.
 * @param responseBody - The response body containing eCR data from S3.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processListS3 = (
  responseBody: ListObjectsV2CommandOutput,
): ListEcr => {
  return (
    responseBody.Contents?.map((object) => {
      return {
        ecrId: object.Key?.replace(".json", "") || "",
        dateModified: object.LastModified
          ? formatDateTime(new Date(object.LastModified!).toISOString())
          : "",
      };
    }) || []
  );
};
