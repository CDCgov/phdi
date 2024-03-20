import { getObservations } from "@/app/labs/utils";
import BundleWithLabs from "../../tests/assets/BundleLabs.json";
import { loadYamlConfig } from "@/app/api/utils";
import { Bundle, Observation } from "fhir/r4";
import BundleWithTravelHistory from "../../tests/assets/BundleTravelHistory.json";
import BundleWithPatient from "../../tests/assets/BundlePatient.json";
import BundleWithEcrMetadata from "../../tests/assets/BundleEcrMetadata.json";
import BundleWithSexualOrientation from "../../tests/assets/BundleSexualOrientation.json";
import BundleWithMiscNotes from "../../tests/assets/BundleMiscNotes.json";
import React from "react";
import { render, screen } from "@testing-library/react";
import exp from "constants";

describe("Labs Utils", () => {
  const mappings = loadYamlConfig();
  describe("getObservations", () => {
    it("extracts an array of observation resources", () => {
      const result = getObservations(
        [
          {
            reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905027",
          },
        ],
        BundleWithLabs as unknown as Bundle,
      );

      const expectedResult = [
        {
          resourceType: "Observation",
          id: "2740f365-7fa7-6a59-ee85-7d6fec905027",
          meta: {
            profile: [
              "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observationresults",
            ],
            source: ["ecr"],
          },
          identifier: [
            {
              system: "urn:oid:1.2.840.114350.1.13.297.3.7.6.798268.2000",
              value: "1670844.7",
            },
          ],
          category: [
            {
              coding: [
                {
                  system:
                    "http://terminology.hl7.org/CodeSystem/observation-category",
                  code: "laboratory",
                },
              ],
            },
          ],
          status: "final",
          code: {
            coding: [
              {
                code: "82204-9",
                display: "E. Coli O157, NAAT",
                system: "http://loinc.org",
              },
            ],
          },
          effectiveDateTime: "2022-09-28T21:00:53Z",
          valueString: "Not Detected",
          extension: [
            {
              url: "http://hl7.org/fhir/R4/specimen.html",
              extension: [
                {
                  url: "specimen source",
                  valueString: "Stool",
                },
                {
                  url: "specimen collection time",
                  valueDateTime: "2022-09-28T20:51:00Z",
                },
                {
                  url: "specimen receive time",
                  valueDateTime: "2022-09-28T20:51:36Z",
                },
                {
                  url: "observation entry reference value",
                  valueString:
                    "#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670844.Comp7",
                },
              ],
            },
          ],
          subject: {
            reference: "Patient/dd326bfb-05e0-49b3-bb62-f2c0e99af6ba",
          },
          performer: [
            {
              display:
                "PROVIDENCE ST. JOSEPH MEDICAL CENTER LABORATORY (CLIA 05D0672675)",
              reference: "Organization/88e344ad-5524-27dc-5803-c49647c531bd",
            },
          ],
        },
      ] as unknown[] as Observation[];
      expect(result.toString()).toBe(expectedResult.toString());
    });

    it("returns an empty array of observation resources if none are found", () => {
      const result = getObservations(
        [
          {
            reference: "Observation/2740f365-7fa7-6a59-ee85-7d6fec905028",
          },
        ],
        BundleWithLabs as unknown as Bundle,
      );
      expect(result).toStrictEqual([]);
    });
  });

  // describe("Evaluate Social Data", () => {
  //   it("should have no available data when there is no data", () => {
  //     const actual = evaluateSocialData(undefined as any, mappings);

  //     expect(actual.availableData).toBeEmpty();
  //     expect(actual.unavailableData).not.toBeEmpty();
  //   });
  //   it("should have travel history when there is a travel history observation present", () => {
  //     const actual = evaluateSocialData(
  //       BundleWithTravelHistory as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual.availableData[0].value)
  //       .toEqualIgnoringWhitespace(`Dates: 2018-01-18 - 2018-02-18
  //          Location(s): Traveled to Singapore, Malaysia and Bali with my family.
  //          Purpose of Travel: Active duty military (occupation)`);
  //   });
  //   it("should have patient sexual orientation when available", () => {
  //     const actual = evaluateSocialData(
  //       BundleWithSexualOrientation as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual.availableData[0].value).toEqual("Do not know");
  //   });
  // });
  // describe("Evaluate Ecr Metadata", () => {
  //   it("should have no available data where there is no data", () => {
  //     const actual = evaluateEcrMetadata(undefined as any, mappings);

  //     expect(actual.ecrSenderDetails.availableData).toBeEmpty();
  //     expect(actual.ecrSenderDetails.unavailableData).not.toBeEmpty();

  //     expect(actual.eicrDetails.availableData).toBeEmpty();
  //     expect(actual.eicrDetails.unavailableData).not.toBeEmpty();

  //     expect(actual.rrDetails.availableData).toBeEmpty();
  //     expect(actual.rrDetails.unavailableData).not.toBeEmpty();
  //   });
  //   it("should have ecrSenderDetails", () => {
  //     const actual = evaluateEcrMetadata(
  //       BundleWithEcrMetadata as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual.ecrSenderDetails.availableData).toEqual([
  //       { title: "Date/Time eCR Created", value: "07/28/2022 10:01 AM EDT" },
  //       {
  //         title: "Sender Facility Name",
  //         value: "Vanderbilt University Adult Hospital",
  //       },
  //       {
  //         title: "Facility Address",
  //         value: "1211 Medical Center Dr\nNashville, TN\n37232",
  //       },
  //       { title: "Facility Contact", value: "+1-615-322-5000" },
  //       { title: "Facility ID", value: "1.2.840.114350.1.13.478.3.7.2.686980" },
  //     ]);
  //     expect(actual.ecrSenderDetails.unavailableData).toEqual([
  //       { title: "Sender Software" },
  //     ]);
  //   });
  //   it("should have eicrDetails", () => {
  //     const actual = evaluateEcrMetadata(
  //       BundleWithEcrMetadata as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual.eicrDetails.availableData).toEqual([
  //       {
  //         title: "eICR Identifier",
  //         value: "1.2.840.114350.1.13.478.3.7.8.688883.230886",
  //       },
  //     ]);
  //     expect(actual.eicrDetails.unavailableData).toBeEmpty();
  //   });
  //   it("should have rrDetails", () => {
  //     const actual = evaluateEcrMetadata(
  //       BundleWithEcrMetadata as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual.rrDetails.availableData).toEqual([
  //       {
  //         title: "Reportable Condition(s)",
  //         value:
  //           "Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)",
  //       },
  //       {
  //         title: "RCKMS Trigger Summary",
  //         value:
  //           "COVID-19 (as a diagnosis or active problem)\nDetection of SARS-CoV-2 nucleic acid in a clinical or post-mortem specimen by any method",
  //       },
  //       {
  //         title: "Jurisdiction(s) Sent eCR",
  //         value: "Tennessee Department of Health",
  //       },
  //     ]);
  //     expect(actual.rrDetails.unavailableData).toBeEmpty();
  //   });
  // });
  // describe("Evaluate Clinical Info", () => {
  //   it("Should return notes", () => {
  //     const actual = evaluateClinicalData(
  //       BundleWithMiscNotes as unknown as Bundle,
  //       mappings,
  //     );
  //     render(actual.clinicalNotes.availableData[0].value as React.JSX.Element);
  //     expect(actual.clinicalNotes.availableData[0].title).toEqual(
  //       "Miscellaneous Notes",
  //     );
  //     expect(screen.getByText("Active Problems")).toBeInTheDocument();
  //     expect(actual.clinicalNotes.unavailableData).toBeEmpty();
  //   });
  // });

  // describe("Evaluate Patient Name", () => {
  //   it("should return name", () => {
  //     const actual = evaluatePatientName(
  //       BundleWithPatient as unknown as Bundle,
  //       mappings,
  //     );
  //     expect(actual).toEqual("ABEL CASTILLO");
  //   });
  // });
  // describe("Extract Patient Address", () => {
  //   it("should return empty string if no address is available", () => {
  //     const actual = extractPatientAddress(undefined as any, mappings);

  //     expect(actual).toBeEmpty();
  //   });
  //   it("should get patient address", () => {
  //     const actual = extractPatientAddress(
  //       BundleWithPatient as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual).toEqual("1050 CARPENTER ST\nEDWARDS, CA\n93523-2800, US");
  //   });
  // });
  // describe("Calculate Patient Age", () => {
  //   it("should return patient age when DOB is available", () => {
  //     // Fixed "today" for testing purposes
  //     jest.useFakeTimers().setSystemTime(new Date("2024-03-12"));

  //     const patientAge = calculatePatientAge(
  //       BundleWithPatient as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(patientAge).toEqual(8);

  //     // Return to real time
  //     jest.useRealTimers();
  //   });
  //   it("should return nothing when DOB is unavailable", () => {
  //     const patientAge = calculatePatientAge(undefined as any, mappings);

  //     expect(patientAge).toEqual(undefined);
  //   });
  // });

  // describe("Extract Patient Address", () => {
  //   it("should return empty string if no address is available", () => {
  //     const actual = extractPatientAddress(undefined as any, mappings);

  //     expect(actual).toBeEmpty();
  //   });
  //   it("should get patient address", () => {
  //     const actual = extractPatientAddress(
  //       BundleWithPatient as unknown as Bundle,
  //       mappings,
  //     );

  //     expect(actual).toEqual("1050 CARPENTER ST\nEDWARDS, CA\n93523-2800, US");
  //   });
  // });
});
