import {
  getObservations,
  searchResultRecord,
  returnFieldValueFromLabHtmlString,
  getLabJsonObject,
  checkAbnormalTag,
} from "@/app/labs/utils";
import { loadYamlConfig } from "@/app/api/utils";
import BundleLabsFinal from "../../tests/assets/BundleLabsFinal.json"; // TODO LABS: Rename BundleLabs
import { Bundle, Observation } from "fhir/r4";
import { evaluate } from "fhirpath";

const pathLabReportAbnormal =
  "Bundle.entry.resource.where(resourceType = 'DiagnosticReport').where(id = '68477c03-5689-f9e5-c267-a3c7bdff6fe0')";
const labReportAbnormal = evaluate(BundleLabsFinal, pathLabReportAbnormal)[0];

const pathLabReportNormal =
  "Bundle.entry.resource.where(resourceType = 'DiagnosticReport').where(id = 'c090d379-9aea-f26e-4ddc-378223841e3b')";
const labReportNormal = evaluate(BundleLabsFinal, pathLabReportNormal)[0];
const labReportNormalJsonObject = {
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
        Value: { value: "Not Detected", metadata: {} },
        "Ref Range": { value: "Not Detected", metadata: {} },
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
        Value: { value: "Not Detected", metadata: {} },
        "Ref Range": { value: "Not Detected", metadata: {} },
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
        "Collection Method / Volume": { value: "", metadata: {} },
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
        "Authorizing Provider": { value: "Ambhp1 Test MD", metadata: {} },
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
        Address: { value: "501 S. Buena Vista Street", metadata: {} },
        "City/State/ZIP Code": {
          value: "Burbank, CA 91505",
          metadata: {},
        },
        "Phone Number": { value: "818-847-6000", metadata: {} },
      },
    ],
  ],
};

describe("Labs Utils", () => {
  const mappings = loadYamlConfig();

  describe("getObservations", () => {
    it("extracts an array of observation resources", () => {
      const result = getObservations(
        {
          result: [
            {
              reference: "Observation/1c0f3367-0588-c90e-fed0-0d8c15c5ac1b",
            },
          ],
        },
        BundleLabsFinal as unknown as Bundle,
        mappings,
      );

      const expectedObservationPath =
        "Bundle.entry.resource.where(resourceType = 'Observation').where(id = '1c0f3367-0588-c90e-fed0-0d8c15c5ac1b')";
      const expectedResult = evaluate(
        BundleLabsFinal,
        expectedObservationPath,
      ) as unknown[] as Observation[];
      expect(result.toString()).toBe(expectedResult.toString());
    });

    it("returns an empty array of observation resources if none are found", () => {
      const result = getObservations(
        {
          result: [
            {
              reference: "Observation/invalid-observation-id",
            },
          ],
        },
        BundleLabsFinal as unknown as Bundle,
        mappings,
      );
      expect(result).toStrictEqual([]);
    });
  });

  describe("getLabJsonObject", () => {
    it("returns correct Json Object", () => {
      const expectedResult = labReportNormalJsonObject;

      const result = getLabJsonObject(
        labReportNormal,
        BundleLabsFinal as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });
  });

  describe("checkAbnormalTag", () => {
    it("should return true if lab report has abnormal tag", () => {
      const expectedResult = true;
      const result = checkAbnormalTag(
        labReportAbnormal,
        BundleLabsFinal as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });

    it("should return false if lab report does not have abnormal tag", () => {
      const expectedResult = false;
      const result = checkAbnormalTag(
        labReportNormal,
        BundleLabsFinal as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });
  });

  describe("searchResultRecord", () => {
    const labHTMLJson = labReportNormalJsonObject.tables;

    it("extracts string of all results of a search for specified lab report", () => {
      const searchKey = "Collection Time";
      const expectedResult = "09/28/2022 1:51 PM PDT";

      const result = searchResultRecord(labHTMLJson, searchKey);

      expect(result).toBe(expectedResult);
    });

    it("returns an empty string of results if none are found for search key", () => {
      const invalidSearchKey = "foobar";
      const expectedResult = "";

      const result = searchResultRecord(labHTMLJson, invalidSearchKey);

      expect(result).toBe(expectedResult);
    });
  });

  describe("returnFieldValueFromLabHtmlString", () => {
    it("extracts correct field value from within a lab report", () => {
      const fieldName = "Analysis Time";
      const expectedResult = "09/28/2022 1:59 PM PDT";

      const result = returnFieldValueFromLabHtmlString(
        labReportNormal,
        BundleLabsFinal as unknown as Bundle,
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
        labReportNormal,
        BundleLabsFinal as unknown as Bundle,
        mappings,
        invalidFieldName,
      );

      expect(result).toStrictEqual(expectedNoData);
    });
  });
});
