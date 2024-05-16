/**
 * @jest-environment node
 */

import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import {
  ListEcr,
  processListS3,
  processListPostgres,
} from "@/app/api/services/listEcrDataService";

describe("listEcrDataService", () => {
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

  describe("processListPostgres", () => {
    it("should return an empty array when responseBody is empty", () => {
      const result = processListPostgres([]);
      expect(result).toEqual([]);
    });

    it("should map each object in responseBody to the correct output structure", () => {
      const responseBody: any[] = [{ ecr_id: "ecr1" }, { ecr_id: "ecr2" }];

      const expected: ListEcr = [
        { ecrId: "ecr1", dateModified: expect.any(String) },
        { ecrId: "ecr2", dateModified: expect.any(String) },
      ];
      const result = processListPostgres(responseBody);

      expect(result).toEqual(expected);
    });
  });
});
