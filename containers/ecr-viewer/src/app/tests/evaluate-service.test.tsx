import {
  evaluateReference,
  evaluateDiagnosticReportData,
} from "@/app/evaluate-service";
import BundleWithMiscNotes from "@/app/tests/assets/BundleMiscNotes.json";
import { Bundle } from "fhir/r4";
import BundleWithPatient from "@/app/tests/assets/BundlePatient.json";
import BundleLabInfo from "@/app/tests/assets/BundleLabInfo.json";
import { loadYamlConfig } from "@/app/api/utils";
import { render, screen } from "@testing-library/react";

const mappings = loadYamlConfig();

describe("Evaluate Reference", () => {
  it("should return undefined if resource not found", () => {
    const actual = evaluateReference(
      BundleWithMiscNotes as unknown as Bundle,
      mappings,
      "Observation/1234",
    );

    expect(actual).toBeUndefined();
  });
  it("should return the resource if the resource is available", () => {
    const actual = evaluateReference(
      BundleWithPatient as unknown as Bundle,
      mappings,
      "Patient/6b6b3c4c-4884-4a96-b6ab-c46406839cea",
    );

    expect(actual.id).toEqual("6b6b3c4c-4884-4a96-b6ab-c46406839cea");
    expect(actual.resourceType).toEqual("Patient");
  });
});

describe("Evaluate Diagnostic Report", () => {
  it("should evaluate diagnostic report title", () => {
    const actual = evaluateDiagnosticReportData(
      BundleLabInfo as unknown as Bundle,
      mappings,
    );

    expect(actual[0].props.title).toContain(
      "Drugs Of Abuse Comprehensive Screen, Ur",
    );
  });
  it("should evaluate diagnostic report results", () => {
    const actual = evaluateDiagnosticReportData(
      BundleLabInfo as unknown as Bundle,
      mappings,
    );

    render(actual[0].props.content);

    expect(screen.getByText("Phencyclidine Screen, Urine")).toBeInTheDocument();
    expect(screen.getByText("Negative")).toBeInTheDocument();
  });
});
