/**
 * @jest-environment node
 */
import {
  listEcrData,
  EcrDisplay,
  processMetadata,
  EcrMetadataModel,
} from "@/app/api/services/listEcrDataService";
import { database } from "../services/db";

describe("listEcrDataService", () => {
  describe("process Metadata", () => {
    it("should return an empty array when responseBody is empty", () => {
      const result = processMetadata([]);
      expect(result).toEqual([]);
    });

    it("should map each object in responseBody to the correct output structure", () => {
      const responseBody: EcrMetadataModel[] = [
        {
          ecr_id: "ecr1",
          date_created: new Date(),
          patient_name_first: "Test",
          patient_name_last: "Person",
          patient_birth_date: new Date(),
          report_date: new Date(),
          condition: "Long",
          rule_summary: "Longer",
          data_source: "DB",
          data: "",
          data_link: "",
        },
        {
          ecr_id: "ecr2",
          date_created: new Date(),
          patient_name_first: "Another",
          patient_name_last: "Test",
          patient_birth_date: new Date(),
          report_date: new Date(),
          condition: "Stuff",
          rule_summary: "Other stuff",
          data_source: "DB",
          data: "",
          data_link: "",
        },
      ];

      const expected: (
        | EcrDisplay
        | {
            rule_summary: any;
            ecrId: string;
            patient_report_date: any;
            date_created: any;
            reportable_condition: any;
            patient_last_name: any;
            patient_date_of_birth: any;
            patient_first_name: any;
          }
        | {
            rule_summary: string;
            ecrId: string;
            patient_report_date: string;
            date_created: any;
            reportable_condition: string;
            patient_last_name: string;
            patient_date_of_birth: string;
            patient_first_name: string;
          }
      )[] = [
        {
          ecrId: "ecr1",
          date_created: expect.any(String),
          patient_first_name: expect.any(String),
          patient_last_name: expect.any(String),
          patient_date_of_birth: expect.any(String),
          patient_report_date: expect.any(String),
          reportable_condition: expect.any(String),
          rule_summary: expect.any(String),
        },
        {
          ecrId: "ecr2",
          date_created: expect.any(String),
          patient_first_name: expect.any(String),
          patient_last_name: expect.any(String),
          patient_date_of_birth: expect.any(String),
          patient_report_date: expect.any(String),
          reportable_condition: expect.any(String),
          rule_summary: expect.any(String),
        },
      ];
      const result = processMetadata(responseBody);

      expect(result).toEqual(expected);
    });
  });

  describe("list Ecr data", () => {
    it("should return empty array when no data is found", async () => {
      let startIndex = 0;
      let itemsPerPage = 25;
      database.manyOrNone = jest.fn(() => Promise.resolve([]));
      const actual = await listEcrData(startIndex, itemsPerPage);
      expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
        "SELECT ed.eICR_ID, ed.patient_name_first, ed.patient_name_last, ed.patient_birth_date, ed.date_created, ed.report_date, erc.condition, ers.rule_summary, ed.report_date FROM ecr_data ed LEFT JOIN ecr_rr_conditions erc ON ed.eICR_ID = erc.eICR_ID LEFT JOIN ecr_rr_rule_summaries ers ON erc.uuid = ers.ecr_rr_conditions_id order by ed.report_date DESC OFFSET 0 ROWS FETCH NEXT 25 ROWS ONLY",
      );
      expect(actual).toBeEmpty();
    });

    it("should return data when found", async () => {
      database.manyOrNone<{ EcrMetadataModel }> = jest.fn(() =>
        Promise.resolve<EcrMetadataModel[]>([
          {
            ecr_id: "1234",
            date_created: new Date("2024-06-21T12:00:00Z"),
            patient_birth_date: new Date("11/07/1954"),
            patient_name_first: "Billy",
            patient_name_last: "Bob",
            report_date: new Date("06/21/2024 8:00 AM EDT"),
            condition: "stuff",
            rule_summary: "yup",
            data: "",
            data_link: "",
            data_source: "DB",
          },
        ]),
      );

      let startIndex = 0;
      let itemsPerPage = 25;
      const actual: EcrDisplay[] = await listEcrData(startIndex, itemsPerPage);

      expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
        "SELECT ed.eICR_ID, ed.patient_name_first, ed.patient_name_last, ed.patient_birth_date, ed.date_created, ed.report_date, erc.condition, ers.rule_summary, ed.report_date FROM ecr_data ed LEFT JOIN ecr_rr_conditions erc ON ed.eICR_ID = erc.eICR_ID LEFT JOIN ecr_rr_rule_summaries ers ON erc.uuid = ers.ecr_rr_conditions_id order by ed.report_date DESC OFFSET 0 ROWS FETCH NEXT 25 ROWS ONLY",
      );
      expect(actual).toEqual([
        {
          date_created: "06/21/2024 8:00 AM EDT",
          ecrId: "1234",
          patient_date_of_birth: "11/07/1954",
          patient_first_name: "Billy",
          patient_last_name: "Bob",
          patient_report_date: "06/21/2024 8:00 AM EDT",
          reportable_condition: "stuff",
          rule_summary: "yup",
        },
      ]);
    });

    it("should get data from the fhir_metadata table", async () => {
      database.manyOrNone<{ EcrMetadataModel }> = jest.fn(() =>
        Promise.resolve<EcrMetadataModel[]>([
          {
            ecr_id: "1234",
            date_created: new Date("2024-06-21T12:00:00Z"),
            patient_name_first: "boy",
            patient_name_last: "lnam",
            patient_birth_date: new Date("1990-01-01T05:00:00.000Z"),
            report_date: new Date("2024-06-20T04:00:00.000Z"),
            condition: "sick",
            rule_summary: "stuff",
            data: "",
            data_link: "",
            data_source: "DB",
          },
        ]),
      );

      let startIndex = 0;
      let itemsPerPage = 25;
      const actual: EcrDisplay[] = await listEcrData(startIndex, itemsPerPage);
      expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
        "SELECT ed.eICR_ID, ed.patient_name_first, ed.patient_name_last, ed.patient_birth_date, ed.date_created, ed.report_date, erc.condition, ers.rule_summary, ed.report_date FROM ecr_data ed LEFT JOIN ecr_rr_conditions erc ON ed.eICR_ID = erc.eICR_ID LEFT JOIN ecr_rr_rule_summaries ers ON erc.uuid = ers.ecr_rr_conditions_id order by ed.report_date DESC OFFSET 0 ROWS FETCH NEXT 25 ROWS ONLY",
      );
      expect(actual).toEqual([
        {
          date_created: "06/21/2024 8:00 AM EDT",
          ecrId: "1234",
          patient_date_of_birth: "01/01/1990",
          patient_first_name: "boy",
          patient_last_name: "lnam",
          patient_report_date: "06/20/2024 12:00 AM EDT",
          reportable_condition: "sick",
          rule_summary: "stuff",
        },
      ]);
    });
  });
});
