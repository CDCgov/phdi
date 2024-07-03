import { AdministeredMedication } from "@/app/view-data/components/AdministeredMedication";
import { render, screen } from "@testing-library/react";
import fs from "fs";
import YAML from "yaml";
import BundleWithPatient from "@/app/tests/assets/BundlePatient.json";
import BundleMedication from "@/app/tests/assets/BundleMedication.json";
import { Bundle } from "fhir/r4";

describe("AdminMedTable", () => {
  const fhirPathFile = fs
    .readFileSync("./src/app/api/fhirPath.yml", "utf8")
    .toString();
  const fhirPathMappings = YAML.parse(fhirPathFile);
  it("should not render anything if there is no administered medications", () => {
    render(
      <AdministeredMedication
        fhirBundle={BundleWithPatient as unknown as Bundle}
        mappings={fhirPathMappings}
      />,
    );

    expect(
      screen.queryByText("Administered Medications"),
    ).not.toBeInTheDocument();
  });

  it("should render administered medications", () => {
    render(
      <AdministeredMedication
        fhirBundle={BundleMedication as unknown as Bundle}
        mappings={fhirPathMappings}
        administeredMedicationReferences={[
          "MedicationAdministration/367be6b3-75f2-2053-63e4-f0a6f1d6bff1",
        ]}
      />,
    );

    expect(screen.getByText("Administered Medications")).toBeVisible();
    expect(screen.getByText("aspirin tablet 325 mg")).toBeVisible();
    expect(screen.getByText("09/29/2022")).toBeVisible();
  });
});
