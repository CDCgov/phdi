import { loadYamlConfig } from "@/app/api/utils";
import BundleLab from "../assets/BundleLab.json";
import { Bundle, Observation } from "fhir/r4";
import { evaluate } from "fhirpath";
import { render, screen } from "@testing-library/react";
import {
  getLabJsonObject,
  getObservations,
  checkAbnormalTag,
  searchResultRecord,
  returnFieldValueFromLabHtmlString,
  evaluateOrganismsReportData,
  evaluateDiagnosticReportData,
  evaluateObservationTable,
  LabReport,
  evaluateLabOrganizationData,
  ResultObject,
  combineOrgAndReportData,
  evaluateLabInfoData,
} from "@/app/services/labsService";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";

const mappings = loadYamlConfig();

const pathLabReportNormal =
  "Bundle.entry.resource.where(resourceType = 'DiagnosticReport').where(id = 'c090d379-9aea-f26e-4ddc-378223841e3b')";
const labReportNormal = evaluate(BundleLab, pathLabReportNormal)[0];
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

const pathLabReportAbnormal =
  "Bundle.entry.resource.where(resourceType = 'DiagnosticReport').where(id = '68477c03-5689-f9e5-c267-a3c7bdff6fe0')";
const labReportAbnormal = evaluate(BundleLab, pathLabReportAbnormal)[0];
const labReportAbnormalJsonObject = getLabJsonObject(
  labReportAbnormal,
  BundleLab as unknown as Bundle,
  mappings,
);

const pathLabOrganismsTableAndNarr =
  "Bundle.entry.resource.where(resourceType = 'DiagnosticReport').where(id = 'b0f590a6-4bf5-7add-9716-2bd3ba6defb2')";
const labOrganismsTableAndNarr = evaluate(
  BundleLab,
  pathLabOrganismsTableAndNarr,
)[0];

describe("Labs Utils", () => {
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
        BundleLab as unknown as Bundle,
        mappings,
      );

      const expectedObservationPath =
        "Bundle.entry.resource.where(resourceType = 'Observation').where(id = '1c0f3367-0588-c90e-fed0-0d8c15c5ac1b')";
      const expectedResult = evaluate(
        BundleLab,
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
        BundleLab as unknown as Bundle,
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
        BundleLab as unknown as Bundle,
        mappings,
      );

      expect(result).toStrictEqual(expectedResult);
    });
  });

  describe("checkAbnormalTag", () => {
    it("should return true if lab report has abnormal tag", () => {
      const expectedResult = true;
      const result = checkAbnormalTag(labReportAbnormalJsonObject);

      expect(result).toStrictEqual(expectedResult);
    });

    it("should return false if lab report does not have abnormal tag", () => {
      const expectedResult = false;
      const result = checkAbnormalTag(labReportNormalJsonObject);

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
        labReportNormalJsonObject,
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
        labReportNormalJsonObject,
        invalidFieldName,
      );

      expect(result).toStrictEqual(expectedNoData);
    });
  });

  describe("evaluateOrganismsReportData", () => {
    it("should return the correct organisms table when the data exists for a lab report", () => {
      const result = evaluateOrganismsReportData(
        labOrganismsTableAndNarr,
        BundleLab as unknown as Bundle,
        mappings,
      )!;
      render(result);

      expect(
        screen.getByText("Avycaz (Ceftazidime/Avibactam)"),
      ).toBeInTheDocument();
      expect(screen.getByText("0.25: Susceptible")).toBeInTheDocument();
      expect(screen.getAllByText("MIC")).toHaveLength(3);
    });
    it("should return undefined if lab organisms data does not exist for a lab report", () => {
      const result = evaluateOrganismsReportData(
        labReportNormal,
        BundleLab as unknown as Bundle,
        mappings,
      );

      expect(result).toBeUndefined();
    });
  });
});

describe("Evaluate Diagnostic Report", () => {
  it("should evaluate diagnostic report title", () => {
    const report = evaluate(BundleLab, mappings["diagnosticReports"])[0];
    const labReportJson = getLabJsonObject(
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actual = evaluateDiagnosticReportData(
      labReportJson,
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<>{actual}</>]}
        organizationId="test"
      />
    );

    expect(actualDisplay.props.title).toContain(
      "STOOL PATHOGENS, NAAT, 12 TO 25 TARGETS",
    );
  });
  it("should evaluate diagnostic report results", () => {
    const report = evaluate(BundleLab, mappings["diagnosticReports"])[0];
    const labReportJson = getLabJsonObject(
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actual = evaluateDiagnosticReportData(
      labReportJson,
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<div key={"1"}>{actual}</div>]}
        organizationId="test"
      />
    );

    render(actualDisplay.props.content);

    expect(screen.getByText("Campylobacter, NAAT")).toBeInTheDocument();
    expect(screen.getAllByText("Not Detected")).not.toBeEmpty();
  });
  it("the table should not appear when there are no results", () => {
    const diagnosticReport = {
      resource: {
        resourceType: "DiagnosticReport",
        code: {
          coding: [
            {
              display: "Drugs Of Abuse Comprehensive Screen, Ur",
            },
          ],
        },
      },
    };
    const actual = evaluateObservationTable(
      diagnosticReport as unknown as LabReport,
      null as unknown as Bundle,
      mappings,
      [],
    );
    expect(actual).toBeUndefined();
  });
  it("should evaluate test method results", () => {
    const report = evaluate(BundleLab, mappings["diagnosticReports"])[0];
    const labReportJson = getLabJsonObject(
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actual = evaluateDiagnosticReportData(
      labReportJson,
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<div key={"1"}>{actual}</div>]}
        organizationId="test"
      />
    );

    render(actualDisplay.props.content);

    expect(
      screen.getAllByText("LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM"),
    ).not.toBeEmpty();
  });
  it("should display comment", () => {
    const report = evaluate(BundleLab, mappings["diagnosticReports"])[2];
    const labReportJson = getLabJsonObject(
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    const actual = evaluateDiagnosticReportData(
      labReportJson,
      report,
      BundleLab as unknown as Bundle,
      mappings,
    );
    render(actual!);

    expect(screen.getByText("View comment")).toBeInTheDocument();
  });
});

describe("Evaluate Organization with ID", () => {
  it("should return a matching org", () => {
    const result = evaluateLabOrganizationData(
      "22c6cdd0-bde1-e220-9ba4-2c2802f795ad",
      BundleLab as unknown as Bundle,
      mappings,
      0,
    );
    expect(result[0].value).toEqual("VUMC CERNER LAB");
  });
  it("should combine the data into new format", () => {
    const testResultObject: ResultObject = {
      "Organization/22c6cdd0-bde1-e220-9ba4-2c2802f795ad": [<div></div>],
    };
    const result = combineOrgAndReportData(
      testResultObject,
      BundleLab as unknown as Bundle,
      mappings,
    );
    expect(result[0].organizationDisplayDataProps).toBeArray();
  });
});

describe("Evaluate the lab info section", () => {
  it("should return a list of objects", () => {
    const result = evaluateLabInfoData(
      BundleLab as unknown as Bundle,
      mappings,
    );
    expect(result[0]).toHaveProperty("diagnosticReportDataElements");
    expect(result[0]).toHaveProperty("organizationDisplayDataProps");
  });
  it("should properly count the number of labs", () => {
    const result = evaluateLabInfoData(
      BundleLab as unknown as Bundle,
      mappings,
    );
    expect(result[0].organizationDisplayDataProps[3].title).toEqual(
      "Number of Results",
    );
    expect(result[0].organizationDisplayDataProps[3].value).toEqual(2);
  });
});
