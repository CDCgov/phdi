import { getObservations, searchResultRecord } from "@/app/labs/utils";
import BundleWithLabs from "../../tests/assets/BundleLabs.json";
import { Bundle, Observation } from "fhir/r4";

describe("Labs Utils", () => {
  describe("getObservations", () => {
    it("extracts an array of observation resources", () => {
      const result = getObservations(
        [
          {
            reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905027",
          },
        ],
        BundleWithLabs as unknown as Bundle,
      );

      const expectedResult = [
        {
          resourceType: "Observation",
          id: "2740f365-7fa7-6a59-ee85-7d6fec905027",
          meta: {
            profile: [
              "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationresults",
            ],
            source: ["ecr"],
          },
          identifier: [
            {
              system: "urn:oid:1.2.840.114350.1.13.297.3.7.6.798268.2000",
              value: "1670844.7",
            },
          ],
          category: [
            {
              coding: [
                {
                  system:
                    "http://terminology.hl7.org/CodeSystem/observation-category",
                  code: "laboratory",
                },
              ],
            },
          ],
          status: "final",
          code: {
            coding: [
              {
                code: "82204-9",
                display: "E. Coli O157, NAAT",
                system: "http://loinc.org",
              },
            ],
          },
          effectiveDateTime: "2022-09-28T21:00:53Z",
          valueString: "Not Detected",
          extension: [
            {
              url: "http://hl7.org/fhir/R4/specimen.html",
              extension: [
                {
                  url: "specimen source",
                  valueString: "Stool",
                },
                {
                  url: "specimen collection time",
                  valueDateTime: "2022-09-28T20:51:00Z",
                },
                {
                  url: "specimen receive time",
                  valueDateTime: "2022-09-28T20:51:36Z",
                },
                {
                  url: "observation entry reference value",
                  valueString:
                    "#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670844.Comp7",
                },
              ],
            },
          ],
          subject: {
            reference: "Patient/dd326bfb-05e0-49b3-bb62-f2c0e99af6ba",
          },
          performer: [
            {
              display:
                "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
              reference: "Organization/88e344ad-5524-27dc-5803-c49647c531bd",
            },
          ],
        },
      ] as unknown[] as Observation[];
      expect(result.toString()).toBe(expectedResult.toString());
    });

    it("returns an empty array of observation resources if none are found", () => {
      const result = getObservations(
        [
          {
            reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905028",
          },
        ],
        BundleWithLabs as unknown as Bundle,
      );
      expect(result).toStrictEqual([]);
    });
  });

  describe("searchResultRecord", () => {
    const labHTLMJson = [
      [
        {
          "Specimen (Source)": {
            value: "Stool",
            metadata: {
              "data-id":
                "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Specimen",
            },
          },
          "Collection Time": {
            value: "09/28/2022 1:51 PM PDT",
            metadata: {},
          },
        },
        {
          "Specimen (Source)": {
            value: "Saliva",
            metadata: {
              "data-id":
                "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Specimen",
            },
          },
          "Collection Time": {
            value: "09/28/2022 2:00 PM PDT",
            metadata: {},
          },
        },
      ],
      [
        {
          "Specimen (Source)": {
            value: "Stool",
            metadata: {
              "data-id":
                "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670850.Specimen",
            },
          },
          "Collection Time": {
            value: "09/29/2022 3:00 PM PDT",
            metadata: {},
          },
        },
        {
          "Specimen (Source)": {
            value: "Saliva",
            metadata: {
              "data-id":
                "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670850.Specimen",
            },
          },
          "Collection Time": {
            value: "09/29/2022 3:05 PM PDT",
            metadata: {},
          },
        },
      ],
    ];

    it("extracts string of all results of a search for specified lab report", () => {
      const searchKey = "Collection Time";
      const ref = "1.2.840.114350.1.13.297.3.7.2.798268.1670845";
      const expectedResult = "09/28/2022 1:51 PM PDT, 09/28/2022 2:00 PM PDT";

      const result = searchResultRecord(labHTLMJson, ref, searchKey);

      expect(result).toBe(expectedResult);
    });

    it("returns an empty string of results if none are found for search key", () => {
      const invalidSearchKey = "foobar";
      const ref = "1.2.840.114350.1.13.297.3.7.2.798268.1670845";
      const expectedResult = "";

      const result = searchResultRecord(labHTLMJson, ref, invalidSearchKey);

      expect(result).toBe(expectedResult);
    });

    it("returns an empty string of results if no lab reports with matching reference ID", () => {
      const searchKey = "Collection Time";
      const invalidRef = "12345";
      const expectedResult = "";

      const result = searchResultRecord(labHTLMJson, invalidRef, searchKey);

      expect(result).toBe(expectedResult);
    });
  });
});
