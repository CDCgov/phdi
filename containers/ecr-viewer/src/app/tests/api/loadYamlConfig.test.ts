import "@testing-library/jest-dom";
import { loadYamlConfig } from "@/app/api/services/utils";

describe("loadYamlConfig", () => {
  it("returns the yaml config", () => {
    const config = loadYamlConfig();
    expect(Object.keys(config).length).toBeGreaterThan(3);
    expect(config["patientGivenName"]).toBe(
      "Bundle.entry.resource.where(resourceType = 'Patient').name.first().given",
    );
  });
});
