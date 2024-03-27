import {
  getObservations,
  searchResultRecord,
  returnFieldValueFromLabHtmlString,
} from "@/app/labs/utils";
import { loadYamlConfig } from "@/app/api/utils";
import BundleWithLabs from "../../tests/assets/BundleLabs.json";
import { Bundle, Observation } from "fhir/r4";

describe("Labs Utils", () => {
  const mappings = loadYamlConfig();
  describe("getObservations", () => {
    it("extracts an array of observation resources", () => {
      const result = getObservations(
        {
          result: [
            {
              reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905027",
            },
          ],
        },
        BundleWithLabs as unknown as Bundle,
        mappings,
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
        {
          result: [
            {
              reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905028",
            },
          ],
        },
        BundleWithLabs as unknown as Bundle,
        mappings,
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
    ];

    it("extracts string of all results of a search for specified lab report", () => {
      const searchKey = "Collection Time";
      const expectedResult = "09/28/2022 1:51 PM PDT, 09/28/2022 2:00 PM PDT";

      const result = searchResultRecord(labHTLMJson, searchKey);

      expect(result).toBe(expectedResult);
    });

    it("returns an empty string of results if none are found for search key", () => {
      const invalidSearchKey = "foobar";
      const expectedResult = "";

      const result = searchResultRecord(labHTLMJson, invalidSearchKey);

      expect(result).toBe(expectedResult);
    });
  });

  describe("returnFieldValueFromLabHtmlString", () => {
    const report = {
      resourceType: "DiagnosticReport",
      id: "68477c03-5689-f9e5-c267-a3c7bdff6fe0",
      identifier: [
        {
          system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.798268",
          value: "1670844",
        },
      ],
      status: "final",
      code: {
        coding: [
          {
            code: "LAB10082",
            display: "STOOL PATHOGENS, NAAT, 12 TO 25 TARGETS",
            system: "http://www.ama-assn.org/go/cpt",
          },
        ],
      },
      effectivePeriod: {
        start: "2022-09-28T20:51:00Z",
        end: "2022-09-28T20:51:00Z",
      },
      subject: {
        reference: "Patient/dd326bfb-05e0-49b3-bb62-f2c0e99af6ba",
      },
      performer: [
        {
          reference: "Organization/9e215f4e-aac1-10cb-e412-020cd13a6ad9",
        },
      ],
      result: [
        {
          reference: "Observation/1c0f3367-0588-c90e-fed0-0d8c15c5ac1b",
        },
        {
          reference: "Observation/ab1ecbd4-6de0-4f78-cea6-a880a15e88bb",
        },
        {
          reference: "Observation/27d88092-54d3-e478-d7e0-24cb7025f783",
        },
        {
          reference: "Observation/dbc917e1-8785-9da8-8c53-df9f84e1b654",
        },
        {
          reference: "Observation/98dac1ba-04ec-0a35-7406-ead6006b12bb",
        },
        {
          reference: "Observation/56fcbbc2-ddd7-a128-f275-be0266218c25",
        },
        {
          reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905027",
        },
        {
          reference: "Observation/fc6d874c-eebb-a244-3fed-71ec18aa1f38",
        },
        {
          reference: "Observation/acf2634c-62f8-df8d-fedf-16f9c44f2e15",
        },
        {
          reference: "Observation/2d0d3912-bf1e-4da8-544b-89355c52dd25",
        },
        {
          reference: "Observation/719c8a9d-196e-4d45-9d83-582a7b3c1fc9",
        },
        {
          reference: "Observation/25c0925a-7fb6-0c36-77c1-2ab174497969",
        },
        {
          reference: "Observation/763b6a78-4b0b-4664-3ca3-005d1dd48422",
        },
        {
          reference: "Observation/bd649a5b-0cbe-a742-277c-897e8163b124",
        },
        {
          reference: "Observation/5e8c2f58-3adc-8f6f-262e-22174c3cb9ae",
        },
        {
          reference: "Observation/9cafcb08-3fa2-f582-e423-80302d5994ef",
        },
        {
          reference: "Observation/88ad5ce6-4050-9628-a560-c0ca8d220a6a",
        },
        {
          reference: "Observation/b6fd9076-66a4-1225-e2bf-701b7b2de43e",
        },
        {
          reference: "Observation/b4cd6618-9a23-c08f-d967-b6a451945de3",
        },
        {
          reference: "Observation/54272272-bd5a-8972-4861-c8aaeb45c57f",
        },
        {
          reference: "Observation/080cfaeb-1e2a-4821-e8e7-de501483f46d",
        },
        {
          reference: "Observation/3d694e5a-92cc-9af5-4365-cfede30abe3c",
        },
      ],
      meta: {
        source: ["ecr"],
      },
    };

    it("extracts correct field value from within a lab report", () => {
      const fieldName = "Analysis Time";
      const expectedResult = "09/28/2022 2:00 PM PDT";

      const result = returnFieldValueFromLabHtmlString(
        report,
        BundleWithLabs as unknown as Bundle,
        mappings,
        fieldName,
      );

      expect(result).toBe(expectedResult);
    });

    it("returns NoData if none are found for field name", () => {
      const invalidFieldName = "foobar";
      const expectedNoData = (
        <span className="no-data text-italic text-base">No data</span>
      );

      const result = returnFieldValueFromLabHtmlString(
        report,
        BundleWithLabs as unknown as Bundle,
        mappings,
        invalidFieldName,
      );

      expect(result).toStrictEqual(expectedNoData);
    });
  });
});
