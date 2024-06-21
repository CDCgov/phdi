import { loadYamlConfig } from "@/app/api/utils";
import { evaluateEcrSummaryRelevantLabResults } from "@/app/services/ecrSummaryService";
import BundleLab from "@/app/tests/assets/BundleLab.json";
import { Bundle } from "fhir/r4";
import { render, screen } from "@testing-library/react";

const mappings = loadYamlConfig();

describe("Evaluate eCR Summary Relevant Lab Results", () => {
  it("should return 'No Data' string when no SNOMED code is provided", () => {
    const expectedValue = "No matching lab results found in this eCR";
    const actual = evaluateEcrSummaryRelevantLabResults(
      BundleLab as unknown as Bundle,
      mappings,
      "",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0]["value"]).toEqual(expectedValue);
  });

  it("should return 'No Data' string when the provided SNOMED code has no matches", () => {
    const expectedValue = "No matching lab results found in this eCR";
    const actual = evaluateEcrSummaryRelevantLabResults(
      BundleLab as unknown as Bundle,
      mappings,
      "invalid-snomed-code",
    );

    expect(actual).toHaveLength(1);
    expect(actual[0]["value"]).toEqual(expectedValue);
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
