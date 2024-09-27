import { evaluateEcrMetadata } from "@/app/services/ecrMetadataService";
import { Bundle } from "fhir/r4";
import BundleWithEcrMetadata from "../assets/BundleEcrMetadata.json";
import { loadYamlConfig } from "@/app/api/utils";

describe("Evaluate Ecr Metadata", () => {
  const mappings = loadYamlConfig();
  it("should have no available data where there is no data", () => {
    const actual = evaluateEcrMetadata(undefined as any, mappings);

    expect(actual.eicrDetails.availableData).toBeEmpty();
    expect(actual.eicrDetails.unavailableData).not.toBeEmpty();

    expect(actual.rrDetails.availableData).toBeUndefined();
  });
  it("should have eicrDetails", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.eicrDetails.availableData).toEqual([
      {
        title: "eICR ID",
        toolTip:
          "Unique document ID for the eICR that originates from the medical record. Different from the Document ID that NBS creates for all incoming records.",
        value: "1.2.840.114350.1.13.478.3.7.8.688883.230886",
      },
      { title: "Date/Time eCR Created", value: "07/28/2022 9:01 AM -05:00" },
      { title: "eICR Release Version", value: "R1.1 (2016-12-01)" },
      { title: "EHR Manufacturer Model Name", value: "Epic - Version 10.1" },
      {
        title: "EHR Software Name",
        toolTip: "EHR system used by the sending provider.",
        value: "Epic - Version 10.1",
      },
    ]);
    expect(actual.eicrDetails.unavailableData).toBeEmpty();
  });
  it("should have eicr Custodian Details", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.ecrCustodianDetails.availableData).toEqual([
      {
        title: "Custodian ID",
        value: "1104202761",
      },
      {
        title: "Custodian Name",
        value: "Vanderbilt University Medical Center",
      },
      {
        title: "Custodian Address",
        value: "3401 West End Ave\nNASHVILLE, TN\n37203, USA",
      },
      {
        title: "Custodian Contact",
        value: "Work 615-322-5000",
      },
    ]);
    expect(actual.ecrCustodianDetails.unavailableData).toBeEmpty();
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
  it("should have eRSDwarnings", () => {
    const actual = evaluateEcrMetadata(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual.eRSDWarnings).toEqual([
      {
        warning:
          "Sending organization is using an outdated eRSD (RCTC) version",
        versionUsed: "2020-06-23",
        expectedVersion:
          "Sending organization should be using one of the following: 2023-10-06, 1.2.2.0, 3.x.x.x.",
        suggestedSolution:
          "The trigger code version your organization is using is out-of-date. Please have your EHR administration install the current version for complete eCR functioning.",
      },
    ]);
  });
});
