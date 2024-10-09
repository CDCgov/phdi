import { loadYamlConfig } from "@/app/api/utils";
import {
  evaluateEncounterId,
  evaluateFacilityId,
  evaluateIdentifiers,
  evaluatePatientRace,
  evaluatePractitionerRoleReference,
  evaluateReference,
  evaluateValue,
} from "@/app/services/evaluateFhirDataService";
import { Bundle } from "fhir/r4";
import BundleWithMiscNotes from "@/app/tests/assets/BundleMiscNotes.json";
import BundleWithPatient from "@/app/tests/assets/BundlePatient.json";
import BundleWithEcrMetadata from "@/app/tests/assets/BundleEcrMetadata.json";
import BundlePractitionerRole from "@/app/tests/assets/BundlePractitionerRole.json";

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

describe("evaluate value", () => {
  it("should provide the string in the case of valueString", () => {
    const actual = evaluateValue(
      { resourceType: "Observation", valueString: "abc" } as any,
      "value",
    );

    expect(actual).toEqual("abc");
  });
  it("should provide the string in the case of valueCodeableConcept", () => {
    const actual = evaluateValue(
      {
        resourceType: "Observation",
        valueCodeableConcept: {
          coding: [
            {
              display: "Negative",
            },
          ],
        },
      } as any,
      "value",
    );

    expect(actual).toEqual("Negative");
  });
  describe("Quantity", () => {
    it("should provide the value and string unit with a space inbetween", () => {
      const actual = evaluateValue(
        {
          resourceType: "Observation",
          valueQuantity: { value: 1, unit: "ft" },
        } as any,
        "value",
      );

      expect(actual).toEqual("1 ft");
    });
    it("should provide the value and symbol unit", () => {
      const actual = evaluateValue(
        {
          resourceType: "Observation",
          valueQuantity: { value: 1, unit: "%" },
        } as any,
        "value",
      );

      expect(actual).toEqual("1%");
    });
  });
});

describe("Evaluate Identifier", () => {
  it("should return the Identifier value", () => {
    const actual = evaluateIdentifiers(
      BundleWithPatient as unknown as Bundle,
      mappings.patientIds,
    );

    expect(actual).toEqual("10308625");
  });
});

describe("Evaluate Patient Race", () => {
  it("should return race category and extension if available", () => {
    const actual = evaluatePatientRace(
      BundleWithPatient as unknown as Bundle,
      mappings,
    );
    expect(actual).toEqual("Black or African American, African");
  });
});

describe("Evaluate Facility Id", () => {
  it("should return the facility id", () => {
    const actual = evaluateFacilityId(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual).toEqual("7162024");
  });
});

describe("Evaluate Encounter ID", () => {
  it("should return the correct Encounter ID", () => {
    const actual = evaluateEncounterId(
      BundleWithEcrMetadata as unknown as Bundle,
      mappings,
    );

    expect(actual).toEqual("1800200448269");
  });
});

describe("Evaluate PractitionerRoleReference", () => {
  it("should return the organization and practitioner when practitioner role is found ", () => {
    const actual = evaluatePractitionerRoleReference(
      BundlePractitionerRole as unknown as Bundle,
      mappings,
      "PractitionerRole/b18c20c1-123b-fd12-71cf-9dd0abae8ced",
    );

    expect(actual.organization).toEqual({
      id: "d319a926-0eb3-5847-3b21-db8b778b4f07",
      name: "Vanderbilt University Medical Center",
      resourceType: "Organization",
    });

    expect(actual.practitioner).toEqual({
      id: "550b9626-bc9e-7d6b-c5d8-e41c2000ab85",
      name: [
        {
          family: "Interface",
        },
      ],
      resourceType: "Practitioner",
    });
  });
  it("should return undefined organization and practitioner when practitioner role is not found", () => {
    const actual = evaluatePractitionerRoleReference(
      BundlePractitionerRole as unknown as Bundle,
      mappings,
      "unknown",
    );

    expect(actual.organization).toBeUndefined();

    expect(actual.practitioner).toBeUndefined();
  });
});
