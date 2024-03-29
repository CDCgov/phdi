import {
  getObservations,
  searchResultRecord,
  returnFieldValueFromLabHtmlString,
  getLabJsonObject,
  checkAbnormalTag,
} from "@/app/labs/utils";
import { loadYamlConfig } from "@/app/api/utils";
import BundleWithLabs from "../../tests/assets/BundleLabs.json";
import { Bundle, Observation } from "fhir/r4";

const diagnosticReportNormal = {
  resourceType: "DiagnosticReport",
  id: "c090d379-9aea-f26e-4ddc-378223841e3b",
  identifier: [
    {
      system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.798268",
      value: "1670845",
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
    reference: "Patient/17a9ed07-6f24-4d91-bada-4dfb28dd76b7",
  },
  performer: [
    {
      reference: "Organization/9e215f4e-aac1-10cb-e412-020cd13a6ad9",
    },
  ],
  result: [
    {
      reference: "Observation/6643fc2a-cbf7-28e9-1331-66a180a09c14",
    },
    {
      reference: "Observation/75bf8f82-8b28-b1bd-e366-cf55b2de0ad9",
    },
    {
      reference: "Observation/7981e6ae-8f87-c93c-efc5-707b8e3f99a0",
    },
    {
      reference: "Observation/9709d136-b5c7-1a47-f61e-ad4d32cd6522",
    },
    {
      reference: "Observation/c5487bdf-17e9-3d00-3243-38ae8c97a413",
    },
    {
      reference: "Observation/e63439ae-5ef1-a25c-894c-8da2f6214102",
    },
    {
      reference: "Observation/94203863-e489-4b09-addf-af39da07f2ac",
    },
    {
      reference: "Observation/9a2897ab-c3e2-2ec8-c17b-41b88437fc32",
    },
    {
      reference: "Observation/729ba013-f503-4b10-3536-f9e709d2858a",
    },
    {
      reference: "Observation/faffdbef-5ec2-c433-60b0-10ae63891c07",
    },
    {
      reference: "Observation/11902558-e412-ceab-678c-7789d59f414c",
    },
    {
      reference: "Observation/7b8e832f-1986-59e2-a169-7f8185d1a4e4",
    },
    {
      reference: "Observation/362c30d1-8015-4ddd-1b8b-bb99a7b40831",
    },
    {
      reference: "Observation/d4cda7f0-a5c7-7f77-eaab-8fc9f303fd70",
    },
    {
      reference: "Observation/1744be52-2a93-ad93-b0c3-8c0114c2399c",
    },
    {
      reference: "Observation/d6fe6a19-fc1c-e45a-f588-7fcac16f4283",
    },
    {
      reference: "Observation/07540f21-e8c1-1675-701c-d3cd686e56b0",
    },
    {
      reference: "Observation/fe118866-7b70-866f-7fcd-909933d2fda0",
    },
    {
      reference: "Observation/c20a6535-5a70-c4ad-fc59-784d65b078d5",
    },
    {
      reference: "Observation/54d662bc-8621-2e20-7542-d21b2b6dbe40",
    },
    {
      reference: "Observation/a3d6cd6c-ef20-8b18-9c50-d62212af9cf0",
    },
  ],
  meta: {
    source: ["ecr"],
  },
};
const diagnosticReportAbnormal = {
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

  describe("getLabJsonObject", () => {
    it("returns correct Json Object", () => {
      const expectedResult = {
        resultId: "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845",
        resultName:
          "Stool Pathogens, NAAT, 12 to 25 Targets (09/28/2022 1:51 PM PDT)",
        tables: [
          [
            {
              Component: {
                value: "Campylobacter, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp1Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp1Signature",
                },
              },
            },
            {
              Component: {
                value: "Plesiomonas shigelloides, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp2Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp2Signature",
                },
              },
            },
            {
              Component: {
                value: "Salmonella, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp3Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp3Signature",
                },
              },
            },
            {
              Component: {
                value: "Vibrio, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp4Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp4Signature",
                },
              },
            },
            {
              Component: {
                value: "Vibrio cholerae, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp5Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp5Signature",
                },
              },
            },
            {
              Component: {
                value: "Yersinia enterocolitica, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp6Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp6Signature",
                },
              },
            },
            {
              Component: {
                value: "E. Coli (EAEC), NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp7Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp7Signature",
                },
              },
            },
            {
              Component: {
                value: "E. Coli (EPEC), NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp8Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp8Signature",
                },
              },
            },
            {
              Component: {
                value: "E. Coli (ETEC), NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp9Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp9Signature",
                },
              },
            },
            {
              Component: {
                value: "Shiga-Like Toxin E. Coli (STEC), NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp10Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp10Signature",
                },
              },
            },
            {
              Component: {
                value: "Shigella/EIEC, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp11Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp11Signature",
                },
              },
            },
            {
              Component: {
                value: "Cryptosporidium, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp12Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp12Signature",
                },
              },
            },
            {
              Component: {
                value: "Cyclospora cayetanensis, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp13Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp13Signature",
                },
              },
            },
            {
              Component: {
                value: "E. histolytica, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp14Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp14Signature",
                },
              },
            },
            {
              Component: {
                value: "Giardia lamblia, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp15Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp15Signature",
                },
              },
            },
            {
              Component: {
                value: "Adenovirus F 40/41, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp16Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp16Signature",
                },
              },
            },
            {
              Component: {
                value: "Astrovirus, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp17Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp17Signature",
                },
              },
            },
            {
              Component: {
                value: "Norovirus, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp18Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp18Signature",
                },
              },
            },
            {
              Component: {
                value: "Rotavirus A, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp19Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp19Signature",
                },
              },
            },
            {
              Component: {
                value: "Sapovirus, NAAT",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp20Name",
                },
              },
              Value: {
                value: "Not Detected",
                metadata: {},
              },
              "Ref Range": {
                value: "Not Detected",
                metadata: {},
              },
              "Test Method": {
                value: "LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM",
                metadata: {},
              },
              "Analysis Time": {
                value: "09/28/2022 1:59 PM PDT",
                metadata: {},
              },
              "Performed At": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {},
              },
              "Pathologist Signature": {
                value: "",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp20Signature",
                },
              },
            },
          ],
          [
            {
              "Specimen (Source)": {
                value: "Stool",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Specimen",
                },
              },
              "Anatomical Location / Laterality": {
                value: "STOOL SPECIMEN / Unknown",
                metadata: {},
              },
              "Collection Method / Volume": {
                value: "",
                metadata: {},
              },
              "Collection Time": {
                value: "09/28/2022 1:51 PM PDT",
                metadata: {},
              },
              "Received Time": {
                value: "09/28/2022 1:51 PM PDT",
                metadata: {},
              },
            },
          ],
          [
            {
              "Authorizing Provider": {
                value: "Ambhp1 Test MD",
                metadata: {},
              },
              "Result Type": {
                value: "MICROBIOLOGY - GENERAL ORDERABLES",
                metadata: {},
              },
            },
          ],
          [
            {
              "Performing Organization": {
                value:
                  "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
                metadata: {
                  "data-id":
                    "Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.PerformingLab",
                },
              },
              Address: {
                value: "501 S. Buena Vista Street",
                metadata: {},
              },
              "City/State/ZIP Code": {
                value: "Burbank, CA 91505",
                metadata: {},
              },
              "Phone Number": {
                value: "818-847-6000",
                metadata: {},
              },
            },
          ],
        ],
      };

      const result = getLabJsonObject(
        diagnosticReportNormal,
        BundleWithLabs as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });
  });

  describe("checkAbnormalTag", () => {
    it("should return true if lab report has abnormal tag", () => {
      const expectedResult = true;
      const result = checkAbnormalTag(
        diagnosticReportAbnormal,
        BundleWithLabs as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });

    it("should return false if lab report does not have abnormal tag", () => {
      const expectedResult = false;
      const result = checkAbnormalTag(
        diagnosticReportNormal,
        BundleWithLabs as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
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
    it("extracts correct field value from within a lab report", () => {
      const fieldName = "Analysis Time";
      const expectedResult = "09/28/2022 1:59 PM PDT";

      const result = returnFieldValueFromLabHtmlString(
        diagnosticReportNormal,
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
        diagnosticReportNormal,
        BundleWithLabs as unknown as Bundle,
        mappings,
        invalidFieldName,
      );

      expect(result).toStrictEqual(expectedNoData);
    });
  });
});
