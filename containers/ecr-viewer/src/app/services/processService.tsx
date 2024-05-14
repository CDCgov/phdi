import { formatDateTime } from "@/app/services/formatService";
import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";

export type ListEcr = {
  ecr_id: string;
  dateModified: string;
}[];

// string constants to match with source values
const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

/**
 * Directs processing a given list of eCRs from different sources based on the source.
 * It supports fetching from S3 and Postgres. If the source is not `postgres` or `s3`,
 * it throws an error stating invalid source.
 * @param responseBody - Response body containing the list of eCRs from either source.
 * @param source - Source of the eCR list (postgres or s3)
 * @returns The array of objects representing the processed list of eCR data.
 * @throws {Error} If the data source is invalid.
 */
export const processListECR = (
  responseBody: any[] | ListObjectsV2CommandOutput,
  source: string,
): ListEcr => {
  let returnBody: ListEcr;
  if (source === S3_SOURCE) {
    returnBody = processListS3(responseBody as ListObjectsV2CommandOutput);
  } else if (source === POSTGRES_SOURCE) {
    returnBody = processListPostgres(responseBody as any[]);
  } else {
    throw new Error("Invalid data source");
  }
  return returnBody;
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
        ecr_id: object.Key?.replace(".json", "") || "",
        dateModified: object.LastModified
          ? formatDateTime(object.LastModified.toString())
          : "",
      };
    }) || []
  );
};

/**
 * Processes a list of eCR data retrieved from Postgres.
 * @param responseBody - The response body containing eCR data from Postgres.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processListPostgres = (responseBody: any[]): ListEcr => {
  return responseBody.map((object) => {
    return {
      ecr_id: object.ecr_id || "",
      dateModified: "N/A",
    };
  });
};
