import { evaluateEcrMetadata } from "@/app/services/ecrMetadataService";
import { Bundle } from "fhir/r4";
import BundleWithEcrMetadata from "../assets/BundleEcrMetadata.json";
import { loadYamlConfig } from "@/app/api/utils";

describe("Evaluate Ecr Metadata", () => {
  const mappings = loadYamlConfig();
  it("should have no available data where there is no data", () => {
    const actual = evaluateEcrMetadata(undefined as any, mappings);
    expect(actual.ecrSenderDetails.availableData).toBeEmpty();
    expect(actual.ecrSenderDetails.unavailableData).not.toBeEmpty();

    expect(actual.eicrDetails.availableData).toBeEmpty();
    expect(actual.eicrDetails.unavailableData).not.toBeEmpty();

    expect(actual.rrDetails.availableData).toBeUndefined();
  });
  it("should have ecrSenderDetails", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.ecrSenderDetails.availableData).toEqual([
      { title: "Date/Time eCR Created", value: "07/28/2022 9:01 AM -05:00" },
      {
        title: "Sender Facility Name",
        value: "Vanderbilt University Adult Hospital",
      },
      {
        title: "Facility Address",
        value: "1211 Medical Center Dr\nNashville, TN\n37232",
      },
      { title: "Facility Contact", value: "+1-615-322-5000" },
      { title: "Facility ID", value: "7162024" },
    ]);
    expect(actual.ecrSenderDetails.unavailableData).toEqual([
      {
        title: "Sender Software",
        toolTip: "EHR system used by the sending provider.",
      },
    ]);
  });
  it("should have eicrDetails", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.eicrDetails.availableData).toEqual([
      {
        title: "eICR Identifier",
        toolTip:
          "Unique document ID for the eICR that originates from the medical record. Different from the Document ID that NBS creates for all incoming records.",
        value: "1.2.840.114350.1.13.478.3.7.8.688883.230886",
      },
      {
        title: "Document Author",
        value: "Vanderbilt University Medical Center",
      },
      {
        title: "Author Address",
        value: "3401 West End Ave\nNASHVILLE, TN\n37203, USA",
      },
      {
        title: "Author Contact",
        value: "Work 615-322-5000",
      },
    ]);
    expect(actual.eicrDetails.unavailableData).toBeEmpty();
  });
  it("should have rrDetails", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.rrDetails).toEqual({
      "Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)":
        {
          "COVID-19 (as a diagnosis or active problem)": new Set([
            "Tennessee Department of Health",
          ]),
          "Detection of SARS-CoV-2 nucleic acid in a clinical or post-mortem specimen by any method":
            new Set(["Tennessee Department of Health"]),
        },
      "Viral hepatitis type C (disorder)": {
        "Detection of Hepatitis C virus antibody in a clinical specimen by any method":
          new Set(["California Department of Public Health"]),
      },
    });
  });
});
