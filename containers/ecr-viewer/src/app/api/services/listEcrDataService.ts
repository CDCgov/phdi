import {
  S3Client,
  ListObjectsV2Command,
  ListObjectsV2CommandOutput,
} from "@aws-sdk/client-s3";
import { database } from "@/app/api/services/db";
import {
  formatDateTime,
  convertUTCToLocalString,
} from "@/app/services/formatService";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const s3Client = new S3Client({ region: process.env.AWS_REGION });

type EcrDataModel = {
  ecr_id: string;
  data: any;
  date_created: string;
};

type EcrMetadataModel = {
  ecr_id: string;
  data_source: "DB" | "S3";
  data_link: string;
  patient_first_name: string;
  patient_last_name: string;
  patient_date_of_birth: Date;
  reportable_condition: string;
  rule_summary: string;
  report_date: Date;
};

type CompleteEcrDataModel = EcrDataModel & EcrMetadataModel;

export type Ecr = {
  ecrId: string;
  dateModified: string;
};

/**
 * Handles GET requests by fetching data from different sources based on the environment configuration.
 * It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
 * a supported source, it returns a JSON response indicating an invalid source.
 * @returns A promise that resolves to a `NextResponse` object
 *   if the source is invalid, or the result of fetching from the specified source.
 *   The specific return type (e.g., the type returned by `list_s3` or `list_postgres`)
 *   may vary based on the source and is thus marked as `unknown`.
 */
export async function listEcrData(): Promise<Ecr[]> {
  if (process.env.SOURCE === S3_SOURCE) {
    const s3Data = await list_s3();
    const processedData = processListS3(s3Data);
    if (process.env.STANDALONE_VIEWER === "true") {
      await getFhirMetadata(processedData);
    }
    return processedData;
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    const data = await list_postgres();
    console.log(data);
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
  let listFhir;
  if (process.env.STANDALONE_VIEWER === "true") {
    listFhir =
      "SELECT fhir.ecr_id, date_created, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC";
  } else {
    listFhir =
      "SELECT ecr_id, date_created FROM fhir order by date_created DESC";
  }
  try {
    if (process.env.STANDALONE_VIEWER === "true") {
      return await database.manyOrNone<CompleteEcrDataModel>(listFhir);
    } else {
      return await database.manyOrNone<EcrDataModel>(listFhir);
    }
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
export const processListPostgres = (responseBody: any[]): Ecr[] => {
  return responseBody.map((object) => {
    return {
      ecrId: object.ecr_id || "",
      dateModified: object.date_created
        ? convertUTCToLocalString(
            formatDateTime(new Date(object.date_created!).toISOString()),
          )
        : "",
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
): Ecr[] => {
  responseBody.Contents?.sort(
    (a, b) => Number(b.LastModified) - Number(a.LastModified),
  );

  return (
    responseBody.Contents?.map((object) => {
      return {
        ecrId: object.Key?.replace(".json", "") || "",
        dateModified: object.LastModified
          ? convertUTCToLocalString(
              formatDateTime(new Date(object.LastModified!).toISOString()),
            )
          : "",
      };
    }) || []
  );
};

/**
 * Fetches eCR Metadata stored in the fhir_metadata table.
 * @param processedData - List of eCR IDs.
 * @returns ecr metadata
 */
const getFhirMetadata = async (
  processedData: Ecr[],
): Promise<EcrMetadataModel[]> => {
  if (process.env.STANDALONE_VIEWER === "true") {
    const ecrIds = processedData.map((ecr) => ecr.ecrId);
    const fhirMetadataQuery =
      "SELECT ecr_id, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition FROM fhir_metadata where ecr_id = $1";

    const data = await database.manyOrNone<EcrMetadataModel>(
      fhirMetadataQuery,
      [ecrIds],
    );
    console.log(data);
    return data;
  } else {
    return [];
  }
};
