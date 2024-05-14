import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import Demographics from "../../view-data/components/Demographics";

describe("Demographics", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const demographicsData = [
      {
        title: "Patient Name",
        value: "Test patient",
      },
      { title: "DOB", value: "06/01/1996" },
      { title: "Current Age", value: "27" },
      { title: "Vital Status", value: "Alive" },
      { title: "Sex", value: "female" },
      { title: "Race", value: "Asian/Pacific Islander" },
      {
        title: "Ethnicity",
        value: "Not Hispanic or Latino",
      },
      {
        title: "Tribal",
        value: "test",
      },
      {
        title: "Preferred Language",
        value: "test",
      },
      {
        title: "Patient Address",
        value: "test address",
      },
      {
        title: "County",
        value: "test",
      },
      { title: "Contact", value: "test contact" },
      {
        title: "Emergency Contact",
        value: "N/A",
      },
      {
        title: "Patient IDs",
        value: "123-4567-890",
      },
    ];
    container = render(
      <Demographics demographicsData={demographicsData} />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
