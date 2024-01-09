import { evaluateSocialData } from "@/app/utils";
import { loadYamlConfig } from "@/app/api/fhir-data/utils";
import { Bundle } from "fhir/r4";

describe("Evaluate Social Data", () => {
  const mappings = loadYamlConfig();
  it("should have no available data when there is no data", () => {
    const actual = evaluateSocialData(undefined, mappings);
    expect(actual.available_data).toBeEmpty();
    expect(actual.unavailable_data).not.toBeEmpty();
  });
  it("should have travel history when there is a travel history observation present", () => {
    const bundleWithTravelHistory = {
      resourceType: "Bundle",
      type: "batch",
      entry: [
        {
          fullUrl: "urn:uuid:595b1386-09d2-7dfb-d414-fb1e5043013d",
          resource: {
            resourceType: "Observation",
            id: "595b1386-09d2-7dfb-d414-fb1e5043013d",
            meta: {
              profile: [
                "http://hl7.org/fhir/us/ecr/StructureDefinition/us-ph-travel-history",
              ],
              source: ["ecr"],
            },
            code: {
              coding: [
                {
                  system: "http://snomed.info/sct",
                  code: "420008001",
                  display: "Travel",
                },
              ],
              text: "Travel History",
            },
            status: "final",
            component: [
              {
                code: {
                  coding: [
                    {
                      system:
                        "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                      code: "LOC",
                      display: "Location",
                    },
                  ],
                },
                valueCodeableConcept: {
                  text: "Traveled to Singapore, Malaysia and Bali with my family.",
                },
              },
              {
                code: {
                  coding: [
                    {
                      system: "http://snomed.info/sct",
                      code: "280147009",
                      display: "Type of activity (attribute)",
                    },
                  ],
                },
                valueCodeableConcept: {
                  coding: [
                    {
                      system: "http://snomed.info/sct",
                      code: "702348006",
                      display: "Active duty military (occupation)",
                    },
                  ],
                },
              },
            ],
            effectivePeriod: {
              start: "2018-01-18",
              end: "2018-02-18",
            },
          },
          request: {
            method: "PUT",
            url: "Observation/595b1386-09d2-7dfb-d414-fb1e5043013d",
          },
        },
      ],
    } as unknown as Bundle;

    const actual = evaluateSocialData(bundleWithTravelHistory, mappings);
    expect(actual.available_data[0].value)
      .toEqualIgnoringWhitespace(`Dates: 2018-01-18 - 2018-02-18
           Location(s): Traveled to Singapore, Malaysia and Bali with my family.
           Purpose of Travel: Active duty military (occupation)`);
  });
});
