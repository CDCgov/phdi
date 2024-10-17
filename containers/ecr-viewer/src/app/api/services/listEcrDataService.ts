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
  condition: string;
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
 * @param startIndex - The index of the first item to fetch
 * @param itemsPerPage - The number of items to fetch
 * @returns A promise resolving to a list of eCR metadata
 */
export async function listEcrData(
  startIndex: number,
  itemsPerPage: number,
): Promise<EcrDisplay[]> {
  const ecrDataQuery =
    "SELECT ed.eICR_ID, ed.patient_name_first, ed.patient_name_last, ed.patient_birth_date, ed.date_created, ed.report_date, erc.condition, ers.rule_summary, ed.report_date FROM ecr_data ed LEFT JOIN ecr_rr_conditions erc ON ed.eICR_ID = erc.eICR_ID LEFT JOIN ecr_rr_rule_summaries ers ON erc.uuid = ers.ecr_rr_conditions_id order by ed.report_date DESC OFFSET " +
    startIndex +
    " ROWS FETCH NEXT " +
    itemsPerPage +
    " ROWS ONLY";
  let list = await database.manyOrNone<EcrMetadataModel>(ecrDataQuery);
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
      reportable_condition: object.condition || "",
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
 * Retrieves the total number of eCRs stored in the ecr_data table.
 * @returns A promise resolving to the total number of eCRs.
 */
export const getTotalEcrCount = async (): Promise<number> => {
  let number = await database.one("SELECT count(*) FROM ecr_data");
  return number.count;
};
