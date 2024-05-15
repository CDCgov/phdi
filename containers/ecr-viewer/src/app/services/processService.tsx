import { formatDateTime } from "@/app/services/formatService";
import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";

export type ListEcr = {
  ecr_id: string;
  dateModified: string;
}[];

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
