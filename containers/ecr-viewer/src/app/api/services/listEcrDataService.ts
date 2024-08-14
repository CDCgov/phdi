import { database } from "@/app/api/services/db";
import {
  convertUTCToLocalString,
  formatDate,
  formatDateTime,
} from "@/app/services/formatService";

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
  date_created: Date;
};

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
  const fhirMetadataQuery =
    "SELECT ecr_id, patient_name_first, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary, date_created FROM fhir_metadata order by date_created DESC OFFSET " +
    startIndex +
    " ROWS FETCH NEXT " +
    itemsPerPage +
    " ROWS ONLY";
  let list = await database.manyOrNone<EcrMetadataModel>(fhirMetadataQuery);
  return processMetadata(list);
}

/**
 * Processes a list of eCR data retrieved from Postgres.
 * @param responseBody - The response body containing eCR data from Postgres.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processMetadata = (
  responseBody: EcrMetadataModel[],
): EcrDisplay[] => {
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
 * Retrieves the total number of eCRs stored in the fhir table.
 * @returns A promise resolving to the total number of eCRs.
 */
export const getTotalEcrCount = async (): Promise<number> => {
  let number = await database.manyOrNone("SELECT count(*) FROM fhir_metadata");
  return number[0].count;
};
