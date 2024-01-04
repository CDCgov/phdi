import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EncounterDetails from "../Encounter";

describe("Encounter", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const encounterData = [
      {
        title: "Facility ID",
        value: "2.16.840.1.113883.4.6",
      },
      {
        title: "Facility Name",
        value: "PRM- Palmdale Regional Medical Center",
      },
      {
        title: "Facility Type",
        value: "Healthcare Provider",
      },
    ];
    const providerData = [
      {
        title: "Provider Name",
        value: "test provider name",
      },
      {
        title: "Provider Contact",
        value: "test provider contact",
      },
    ];
    container = render(
      <EncounterDetails
        encounterData={encounterData}
        providerData={providerData}
      />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
