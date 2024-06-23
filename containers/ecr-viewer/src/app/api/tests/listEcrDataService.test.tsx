/**
 * @jest-environment node
 */

import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import {
  ListEcr,
  processListS3,
  processListPostgres,
  listEcrData,
} from "@/app/api/services/listEcrDataService";
import { database } from "../services/db";

describe("listEcrDataService", () => {
  let log = jest.spyOn(console, "log").mockImplementation(() => {});
  afterEach(() => {
    log.mockReset();
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

      const expected: ListEcr = [
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
      const responseBody: any[] = [
        { ecr_id: "ecr1", date_created: new Date() },
        { ecr_id: "ecr2", date_created: new Date() },
      ];

      const expected: ListEcr = [
        { ecrId: "ecr1", dateModified: expect.any(String) },
        { ecrId: "ecr2", dateModified: expect.any(String) },
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
      "SELECT fhir.ecr_id, date_created, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
    );
    expect(actual).toBeEmpty();
  });

  it("should return data when found and source is postgres", async () => {
    process.env.SOURCE = "postgres";
    database.manyOrNone<{ ecr_id: string; date_created: string }> = jest.fn(
      () =>
        Promise.resolve([
          { ecr_id: "1234", date_created: "2024-06-21T12:00:00Z" },
        ]),
    );

    const actual = await listEcrData();

    expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
      "SELECT fhir.ecr_id, date_created, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
    );
    expect(actual).toEqual([
      {
        dateModified: "06/21/2024 8:00 AM EDT",
        ecrId: "1234",
      },
    ]);
  });

  it("should console log data from the fhir_metadata table", async () => {
    process.env.SOURCE = "postgres";
    database.manyOrNone<{ ecr_id: string; date_created: string }> = jest.fn(
      () =>
        Promise.resolve([
          {
            ecr_id: "1234",
            date_created: "2024-06-21T12:00:00Z",
            patient_name_last: "lnam",
            patient_birth_date: "1990-01-01T05:00:00.000Z",
            report_date: "2024-06-20T04:00:00.000Z",
            reportable_condition: "sick",
          },
        ]),
    );

    const actual = await listEcrData();

    expect(database.manyOrNone).toHaveBeenCalledExactlyOnceWith(
      "SELECT fhir.ecr_id, date_created, patient_name_last, patient_name_last, patient_birth_date, report_date, reportable_condition FROM fhir LEFT OUTER JOIN fhir_metadata on fhir.ecr_id = fhir_metadata.ecr_id order by date_created DESC",
    );
    expect(actual).toEqual([
      {
        dateModified: "06/21/2024 8:00 AM EDT",
        ecrId: "1234",
      },
    ]);
    expect(log).toHaveBeenCalledExactlyOnceWith([
      {
        ecr_id: "1234",
        date_created: "2024-06-21T12:00:00Z",
        patient_name_last: "lnam",
        patient_birth_date: "1990-01-01T05:00:00.000Z",
        report_date: "2024-06-20T04:00:00.000Z",
        reportable_condition: "sick",
      },
    ]);
  });
});
