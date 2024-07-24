import { loadYamlConfig } from "@/app/api/utils";
import {
  evaluateEcrSummaryConditionSummary,
  evaluateEcrSummaryRelevantClinicalDetails,
} from "@/app/services/ecrSummaryService";
import BundleWithClinicalInfo from "@/app/tests/assets/BundleClinicalInfo.json";
import { evaluateEcrSummaryRelevantLabResults } from "@/app/services/ecrSummaryService";
import BundleLab from "@/app/tests/assets/BundleLab.json";
import BundleEcrSummary from "@/app/tests/assets/BundleEcrSummary.json";
import { Bundle } from "fhir/r4";
import { render, screen } from "@testing-library/react";
import React from "react";

const mappings = loadYamlConfig();

describe("Evaluate eCR Summary Relevant Clinical Details", () => {
  it("should return 'No Data' string when no SNOMED code is provided", () => {
    const expectedValue = "No matching clinical data found in this eCR";
    const actual = evaluateEcrSummaryRelevantClinicalDetails(
      BundleWithClinicalInfo as unknown as Bundle,
      mappings,
      "",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0].value).toEqual(expectedValue);
  });

  it("should return 'No Data' string when the provided SNOMED code has no matches", () => {
    const expectedValue = "No matching clinical data found in this eCR";
    const actual = evaluateEcrSummaryRelevantClinicalDetails(
      BundleWithClinicalInfo as unknown as Bundle,
      mappings,
      "invalid-snomed-code",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0].value).toEqual(expectedValue);
  });

  it("should return the correct active problem when the provided SNOMED code matches", () => {
    const result = evaluateEcrSummaryRelevantClinicalDetails(
      BundleWithClinicalInfo as unknown as Bundle,
      mappings,
      "263133002",
    );
    expect(result).toHaveLength(1);

    render(result[0].value);
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(
      screen.getByText("Sprain of calcaneofibular ligament of right ankle"),
    ).toBeInTheDocument();
    expect(screen.getByText("04/16/2019")).toBeInTheDocument();

    // Active problem(s) without a matching SNOMED code should not be included
    expect(screen.queryByText("Knee pain")).not.toBeInTheDocument();
  });
});

describe("Evaluate eCR Summary Relevant Lab Results", () => {
  it("should return 'No Data' string when no SNOMED code is provided", () => {
    const expectedValue = "No matching lab results found in this eCR";
    const actual = evaluateEcrSummaryRelevantLabResults(
      BundleLab as unknown as Bundle,
      mappings,
      "",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0].value).toEqual(expectedValue);
  });

  it("should return 'No Data' string when the provided SNOMED code has no matches", () => {
    const expectedValue = "No matching lab results found in this eCR";
    const actual = evaluateEcrSummaryRelevantLabResults(
      BundleLab as unknown as Bundle,
      mappings,
      "invalid-snomed-code",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0].value).toEqual(expectedValue);
  });

  it("should return the correct lab result(s) when the provided SNOMED code matches", () => {
    const result = evaluateEcrSummaryRelevantLabResults(
      BundleLab as unknown as Bundle,
      mappings,
      "test-snomed",
    );
    expect(result).toHaveLength(3); // 2 results, plus last item is divider line

    render(result[0].value);
    expect(screen.getByRole("button")).toBeInTheDocument();
    expect(
      screen.getByText("STOOL PATHOGENS, NAAT, 12 TO 25 TARGETS"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("09/28/2022 8:51 PM UTC")).toHaveLength(2);

    render(result[1].value);
    expect(screen.getByText("Cytogenomic SNP microarray")).toBeInTheDocument();
  });
});

describe("evaluateEcrSummaryConditionSummary", () => {
  it("should return titles based on snomed code", () => {
    const actual = evaluateEcrSummaryConditionSummary(
      BundleEcrSummary as unknown as Bundle,
      mappings,
    );

    expect(actual[0].title).toEqual("Viral hepatitis type C (disorder)");
    expect(actual[1].title).toEqual(
      "Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
    );
  });
  it("should return summaries based on snomed code", () => {
    const actual = evaluateEcrSummaryConditionSummary(
      BundleEcrSummary as unknown as Bundle,
      mappings,
    );
    render(
      actual[1].conditionDetails.map((detail) => (
        <React.Fragment key={detail.title}>{detail.value}</React.Fragment>
      )),
    );

    expect(
      screen.queryByText(
        "Detection of Hepatitis C virus antibody in a clinical specimen by any method",
      ),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText("COVID-19 (as a diagnosis or active problem)"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Detection of SARS-CoV-2 nucleic acid in a clinical or post-mortem specimen by any method",
      ),
    ).toBeInTheDocument();
  });
  it("should return clinical details based on snomed code", () => {
    const actual = evaluateEcrSummaryConditionSummary(
      BundleEcrSummary as unknown as Bundle,
      mappings,
    );

    render(
      actual[1].clinicalDetails.map((detail) => (
        <div key={Math.random()}>{detail.value}</div>
      )),
    );

    expect(screen.getByText("COVID toes")).toBeInTheDocument();
  });
  it("should return lab details based on snomed code", () => {
    const actual = evaluateEcrSummaryConditionSummary(
      BundleEcrSummary as unknown as Bundle,
      mappings,
    );

    render(
      actual[1].labDetails.map((detail) => (
        <React.Fragment key={Math.random()}>{detail.value}</React.Fragment>
      )),
    );

    expect(
      screen.queryByText("No matching lab results found in this eCR"),
    ).not.toBeInTheDocument();
    expect(screen.getByText("SARS-CoV-2 PCR")).toBeInTheDocument();
  });
  it("Should return empty array if none found", () => {
    const actual = evaluateEcrSummaryConditionSummary({} as Bundle, mappings);

    expect(actual).toBeEmpty();
  });
});
