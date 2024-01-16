import { evaluateSocialData } from "@/app/utils";
import { loadYamlConfig } from "@/app/api/fhir-data/utils";
import { Bundle } from "fhir/r4";
import BundleWithTravelHistory from "../tests/assets/BundleTravelHistory.json"
describe("Evaluate Social Data", () => {
  const mappings = loadYamlConfig();
  it("should have no available data when there is no data", () => {
    const actual = evaluateSocialData(undefined, mappings);
    expect(actual.available_data).toBeEmpty();
    expect(actual.unavailable_data).not.toBeEmpty();
  });
  it("should have travel history when there is a travel history observation present", () => {
    const actual = evaluateSocialData(BundleWithTravelHistory as unknown as Bundle, mappings);
    expect(actual.available_data[0].value)
      .toEqualIgnoringWhitespace(`Dates: 2018-01-18 - 2018-02-18
           Location(s): Traveled to Singapore, Malaysia and Bali with my family.
           Purpose of Travel: Active duty military (occupation)`);
  });
});
