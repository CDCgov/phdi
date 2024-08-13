import {
  S3Client,
  ListObjectsV2Command,
  ListObjectsV2CommandOutput,
} from "@aws-sdk/client-s3";
import { database } from "@/app/api/services/db";
import {
  formatDateTime,
  convertUTCToLocalString,
  formatDate,
} from "@/app/services/formatService";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const s3Client = new S3Client({ region: process.env.AWS_REGION });

export type EcrDataModel = {
  ecr_id: string;
  data: any;
  date_created: string;
};

export type EcrMetadataModel = {
  ecr_id: string;
  data_source: "DB" | "S3";
  data_link: string;
  patient_name_first: string;
  patient_name_last: string;
  patient_birth_date: Date;
  reportable_condition: string;
  rule_summary: string;
  report_date: Date;
};

export type CompleteEcrDataModel = EcrDataModel & EcrMetadataModel;

export type EcrDisplay = {
  ecrId: string;
  patient_first_name: string;
  patient_last_name: string;
  patient_date_of_birth: string | undefined;
  reportable_condition: string;
  rule_summary: string;
  patient_report_date: string;
  date_created: string;
};

/**
 * Handles GET requests by fetching data from different sources based on the environment configuration.
 * It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
 * a supported source, it returns a JSON response indicating an invalid source.
 * @param startIndex - The index of the first item to fetch
 * @param itemsPerPage - The number of items to fetch
 * @returns A promise that resolves to a `NextResponse` object
 *   if the source is invalid, or the result of fetching from the specified source.
 *   The specific return type (e.g., the type returned by `list_s3` or `list_postgres`)
 *   may vary based on the source and is thus marked as `unknown`.
 */
export async function listEcrData(
  startIndex: number,
  itemsPerPage: number,
): Promise<EcrDisplay[]> {
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";
  if (process.env.SOURCE === S3_SOURCE) {
    const s3Data = await list_s3(startIndex, itemsPerPage);
    const processedData = processListS3(s3Data);
    if (isNonIntegratedViewer) {
      await getFhirMetadata(processedData);
    }
    return processedData;
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    const data = await list_postgres(startIndex, itemsPerPage);
    return processListPostgres(data);
  } else {
    throw Error("Invalid Source");
  }
}

/**
 * Retrieves array of eCR IDs from PostgreSQL database.
 * @param startIndex - The index of the first item to fetch
 * @param itemsPerPage - The number of items to fetch
 * @returns A promise resolving to a NextResponse object.
 */
const list_postgres = async (startIndex: number, itemsPerPage: number) => {
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";
  try {
    if (isNonIntegratedViewer) {
      let listFhir =
        "SELECT fhir.ecr_id, date_created, patient_name_first, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC OFFSET " +
        startIndex +
        " ROWS FETCH NEXT " +
        itemsPerPage +
        " ROWS ONLY";
      return await database.manyOrNone<CompleteEcrDataModel>(listFhir);
    } else {
      let listFhir =
        "SELECT ecr_id, date_created FROM fhir order by date_created DESC";
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
 * @param startIndex - The index of the first item to fetch
 * @param itemsPerPage - The number of items to fetch
 * @returns A promise resolving to a NextResponse object.
 */
const list_s3 = async (startIndex: number, itemsPerPage: number) => {
  const bucketName = process.env.ECR_BUCKET_NAME;

  try {
    const command = new ListObjectsV2Command({
      Bucket: bucketName,
      //StartAfter: startIndex.toString(),
      MaxKeys: itemsPerPage,
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
export const processListPostgres = (responseBody: any[]): EcrDisplay[] => {
  return responseBody.map((object) => {
    return {
      ecrId: object.ecr_id || "",
      patient_first_name: object.patient_name_first || "",
      patient_last_name: object.patient_name_last || "",
      patient_date_of_birth: object.patient_birth_date
        ? formatDate(new Date(object.patient_birth_date!).toISOString())
        : "",
      reportable_condition: object.reportable_condition || "",
      rule_summary: object.rule_summary || "",
      date_created: object.date_created
        ? convertUTCToLocalString(
            formatDateTime(new Date(object.date_created!).toISOString()),
          )
        : "",
      patient_report_date: object.report_date
        ? convertUTCToLocalString(
            formatDateTime(new Date(object.report_date!).toISOString()),
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
): any[] => {
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
  processedData: EcrDisplay[],
): Promise<EcrMetadataModel[]> => {
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";
  if (isNonIntegratedViewer) {
    const ecrIds = processedData.map((ecr) => ecr.ecrId);
    const fhirMetadataQuery =
      "SELECT ecr_id, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary FROM fhir_metadata where ecr_id = $1";

    const data = await database.manyOrNone<EcrMetadataModel>(
      fhirMetadataQuery,
      [ecrIds],
    );
    return data;
  } else {
    return [];
  }
};

/**
 * Retrieves the total number of eCRs stored in the fhir table.
 * @returns A promise resolving to the total number of eCRs.
 */
export const getTotalEcrCount = async (): Promise<number> => {
  if (process.env.SOURCE === S3_SOURCE) {
    const bucketName = process.env.ECR_BUCKET_NAME;
    const command = new ListObjectsV2Command({
      Bucket: bucketName,
    });
    let listS3 = s3Client.send(command);
    return listS3.Contents?.length || 0;
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    let number = await database.manyOrNone("SELECT count(*) FROM fhir");
    return number[0].count;
  } else {
    return 0;
  }
};
