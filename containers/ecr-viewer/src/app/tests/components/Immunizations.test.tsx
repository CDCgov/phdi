import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import fs from "fs";
import YAML from "yaml";
import { Bundle, Immunization } from "fhir/r4";
import BundleClinicalInfo from "@/app/tests/assets/BundleClinicalInfo.json";
import { returnImmunizations } from "@/app/view-data/components/common";

describe("Immunizations Table", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const fhirPathFile = fs
      .readFileSync("./src/app/api/fhirPath.yml", "utf8")
      .toString();
    const fhirPathMappings = YAML.parse(fhirPathFile);

    const immunizationsData = [
      {
        id: "7a4b0e4b-ca8a-a39b-1b44-19efe2c9ee5c",
        meta: {
          source: ["ecr"],
        },
        note: {
          text: "DTAP-HIB-IPV (PENTACEL)",
        },
        status: "completed",
        identifier: [
          {
            value: "35371",
            system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.768076",
          },
        ],
        resourceType: "Immunization",
        primarySource: true,
        occurrenceDateTime: "04/16/2010",
      },
      {
        id: "b5d003f7-cfe2-56a4-6e91-07307f25aa83",
        meta: {
          source: ["ecr"],
        },
        note: {
          text: "TDAP, (ADOL/ADULT)",
        },
        status: "completed",
        patient: {
          reference: "Patient/d2ff4c14-a41b-47f6-9038-6aabfd655ad5",
        },
        identifier: [
          {
            value: "57643",
            system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.768076",
          },
        ],
        vaccineCode: {
          coding: [
            {
              code: "49281-400-10",
              system: "urn:oid:2.16.840.1.113883.6.69",
            },
          ],
        },
        resourceType: "Immunization",
        primarySource: true,
        occurrenceDateTime: "11/10/2020",
        lotNumber: "369258741",
        manufacturer: {
          reference: "Organization/b5c77b86-2764-79f9-10bf-5da5e63eb7c1",
        },
        protocolApplied: [
          {
            doseNumberPositiveInt: "1",
          },
        ],
      },
      {
        id: "cffb2ab8-483c-a93e-56c3-5cc3d11e9168",
        meta: {
          source: ["ecr"],
        },
        note: {
          text: "HEP A (ADULT) 2 DOSE",
        },
        status: "completed",
        identifier: [
          {
            value: "57644",
            system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.768076",
          },
        ],
        resourceType: "Immunization",
        primarySource: true,
        occurrenceDateTime: "11/11/2011",
      },
      {
        id: "35c0d7fc-0bc0-5a24-e65e-dc30321d7e2e",
        meta: {
          source: ["ecr"],
        },
        note: {
          text: "MENINGOCOCCAL CONJUGATE,MENACTRA                                        (PED/ADOL/ADULT)",
        },
        status: "completed",
        patient: {
          reference: "Patient/d2ff4c14-a41b-47f6-9038-6aabfd655ad5",
        },
        identifier: [
          {
            value: "58353",
            system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.768076",
          },
        ],
        vaccineCode: {
          coding: [
            {
              code: "50090-1890-1",
              system: "urn:oid:2.16.840.1.113883.6.69",
            },
          ],
        },
        resourceType: "Immunization",
        primarySource: true,
        occurrenceDateTime: "11/16/2020",
      },
      {
        id: "50fc36a0-b859-c4a4-de8f-53c149080081",
        meta: {
          source: ["ecr"],
        },
        note: {
          text: "HEP B (PED,ADOLESCENT) 3 DOSE",
        },
        status: "completed",
        identifier: [
          {
            value: "58354",
            system: "urn:oid:1.2.840.114350.1.13.297.3.7.2.768076",
          },
        ],
        resourceType: "Immunization",
        primarySource: true,
        occurrenceDateTime: "03/21/1974",
      },
    ] as unknown as Immunization[];

    container = render(
      returnImmunizations(
        BundleClinicalInfo as unknown as Bundle,
        immunizationsData,
        fhirPathMappings,
      )!,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
