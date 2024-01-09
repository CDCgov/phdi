import { evaluateSocialData } from "@/app/utils";
import { loadYamlConfig } from "@/app/api/fhir-data/utils";

describe("Evaluate Social Data", () =>{
  const mappings = loadYamlConfig();
  it("should have no available data when there is no data", () => {
    expect(evaluateSocialData(undefined, mappings).available_data).toBeEmpty();
    expect(evaluateSocialData(undefined, mappings).unavailable_data).not.toBeEmpty();
  })
})