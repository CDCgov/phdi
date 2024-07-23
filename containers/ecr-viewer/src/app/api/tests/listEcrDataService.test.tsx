/**
 * @jest-environment node
 */

import {
  ListObjectsV2Command,
  ListObjectsV2CommandOutput,
  S3Client,
} from "@aws-sdk/client-s3";
import {
  processListS3,
  processListPostgres,
  listEcrData,
  EcrDisplay,
  CompleteEcrDataModel,
} from "@/app/api/services/listEcrDataService";
import { database } from "../services/db";
import { mockClient } from "aws-sdk-client-mock";

const s3Mock = mockClient(S3Client);

describe("listEcrDataService", () => {
  let log = jest.spyOn(console, "log").mockImplementation(() => {});
  beforeEach(() => {
    log.mockReset();
    s3Mock.reset();
  });

  describe("processListS3", () => {
    it("should return an empty array when responseBody is empty", () => {
      const responseBody: ListObjectsV2CommandOutput = {
        $metadata: {},
        Contents: [],
      };

      const result = processListS3(responseBody);
      expect(result).toEqual([]);
    });

    it("should map each object in responseBody to the correct output structure", () => {
      const responseBody: ListObjectsV2CommandOutput = {
        $metadata: {},
        Contents: [
          { Key: "ecr1.json", LastModified: new Date() },
          { Key: "ecr2.json", LastModified: new Date() },
        ],
      };

      const expected: EcrDisplay[] = [
        { ecrId: "ecr1", dateModified: expect.any(String) },
        { ecrId: "ecr2", dateModified: expect.any(String) },
      ];
      const result = processListS3(responseBody);

      expect(result).toEqual(expected);
    });
  });

  it("should sort objects by LastModified in descending order", () => {
    const date1 = new Date("2023-01-01T12:00:00Z");
    const date2 = new Date("2023-01-02T12:00:00Z");
    const responseBody = {
      $metadata: {},
      Contents: [
        { Key: "ecr1.json", LastModified: date1 },
        { Key: "ecr2.json", LastModified: date2 },
      ],
    };

    const expected = [
      { ecrId: "ecr2", dateModified: "01/02/2023 7:00 AM EST" },
      { ecrId: "ecr1", dateModified: "01/01/2023 7:00 AM EST" },
    ];
    const result = processListS3(responseBody);

    expect(result).toEqual(expected);
  });

  describe("processListPostgres", () => {
    it("should return an empty array when responseBody is empty", () => {
      const result = processListPostgres([]);
      expect(result).toEqual([]);
    });

    it("should map each object in responseBody to the correct output structure", () => {
      const responseBody: CompleteEcrDataModel[] = [
        {
          ecr_id: "ecr1",
          date_created: "10/11/1999",
          patient_name_first: "Test",
          patient_name_last: "Person",
          patient_birth_date: new Date(),
          report_date: new Date(),
          reportable_condition: "Long",
          rule_summary: "Longer",
          data_source: "DB",
          data: "",
          data_link: "",
        },
        {
          ecr_id: "ecr2",
          date_created: "04/22/1989",
          patient_name_first: "Another",
          patient_name_last: "Test",
          patient_birth_date: new Date(),
          report_date: new Date(),
          reportable_condition: "Stuff",
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
      const result = processListPostgres(responseBody);

      expect(result).toEqual(expected);
    });
  });

  it("should return empty array when no data is found and source is postgres", async () => {
    process.env.SOURCE = "postgres";
    database.manyOrNone = jest.fn(() => Promise.resolve([]));
    const actual = await listEcrData();
    expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
      "SELECT fhir.ecr_id, date_created, patient_name_first, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
    );
    expect(actual).toBeEmpty();
  });

  it("should return data when found and source is postgres", async () => {
    process.env.SOURCE = "postgres";
    database.manyOrNone<{
      ecr_id: string;
      date_created: string;
      patient_birth_date: string;
      patient_name_first: string;
      patient_name_last: string;
      report_date: string;
      reportable_condition: string;
      rule_summary: string;
    }> = jest.fn(() =>
      Promise.resolve<CompleteEcrDataModel[]>([
        {
          ecr_id: "1234",
          date_created: "2024-06-21T12:00:00Z",
          patient_birth_date: new Date("11/07/1954"),
          patient_name_first: "Billy",
          patient_name_last: "Bob",
          report_date: new Date("06/21/2024 8:00 AM EDT"),
          reportable_condition: "stuff",
          rule_summary: "yup",
          data: "",
          data_link: "",
          data_source: "DB",
        },
      ]),
    );

    const actual: EcrDisplay[] = await listEcrData();

    expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
      "SELECT fhir.ecr_id, date_created, patient_name_first, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
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

  it("should console log data from the fhir_metadata table", async () => {
    process.env.SOURCE = "postgres";
    database.manyOrNone<{
      ecr_id: string;
      date_created: string;
      patient_birth_date: string;
      patient_name_first: string;
      patient_name_last: string;
      report_date: string;
      reportable_condition: string;
      rule_summary: string;
    }> = jest.fn(() =>
      Promise.resolve<CompleteEcrDataModel[]>([
        {
          ecr_id: "1234",
          date_created: "2024-06-21T12:00:00Z",
          patient_name_first: "boy",
          patient_name_last: "lnam",
          patient_birth_date: new Date("1990-01-01T05:00:00.000Z"),
          report_date: new Date("2024-06-20T04:00:00.000Z"),
          reportable_condition: "sick",
          rule_summary: "stuff",
          data: "",
          data_link: "",
          data_source: "DB",
        },
      ]),
    );

    const actual: EcrDisplay[] = await listEcrData();

    expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
      "SELECT fhir.ecr_id, date_created, patient_name_first, patient_name_last, patient_birth_date, report_date, reportable_condition, rule_summary FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
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
    expect(log).toHaveBeenCalledExactlyOnceWith([
      {
        date_created: "2024-06-21T12:00:00Z",
        ecr_id: "1234",
        patient_birth_date: new Date("1990-01-01T05:00:00.000Z"),
        patient_name_first: "boy",
        patient_name_last: "lnam",
        report_date: new Date("2024-06-20T04:00:00.000Z"),
        reportable_condition: "sick",
        rule_summary: "stuff",
        data: "",
        data_link: "",
        data_source: "DB",
      },
    ]);
  });

  describe("getS3", () => {
    it("should return data from S3", async () => {
      process.env.SOURCE = "s3";
      s3Mock.on(ListObjectsV2Command).resolves({
        Contents: [
          { Key: "id1", LastModified: new Date("2024-06-23T12:00:00Z") },
        ],
      });
      const actual = await listEcrData();

      expect(actual).toEqual([
        {
          dateModified: "06/23/2024 8:00 AM EDT",
          ecrId: "id1",
        },
      ]);
    });
    it("should fetch FHIR Metadata", async () => {
      process.env.SOURCE = "s3";
      s3Mock.on(ListObjectsV2Command).resolves({
        Contents: [
          { Key: "id1", LastModified: new Date("2024-06-23T12:00:00Z") },
        ],
      });
      database.manyOrNone<{ ecr_id: string; date_created: string }> = jest.fn(
        () =>
          Promise.resolve([
            {
              ecr_id: "id1",
              date_created: "2024-06-21T12:00:00Z",
              patient_name_last: "lnam",
              patient_birth_date: "1990-01-01T05:00:00.000Z",
              report_date: "2024-06-20T04:00:00.000Z",
              reportable_condition: "sick",
            },
          ]),
      );

      const actual = await listEcrData();

      expect(actual).toEqual([
        {
          dateModified: "06/23/2024 8:00 AM EDT",
          ecrId: "id1",
        },
      ]);
      expect(log).toHaveBeenCalledExactlyOnceWith([
        {
          ecr_id: "id1",
          date_created: "2024-06-21T12:00:00Z",
          patient_name_last: "lnam",
          patient_birth_date: "1990-01-01T05:00:00.000Z",
          report_date: "2024-06-20T04:00:00.000Z",
          reportable_condition: "sick",
        },
      ]);
    });
  });
});
