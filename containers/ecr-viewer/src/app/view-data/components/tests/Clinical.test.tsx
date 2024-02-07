import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import ClinicalInfo from "../ClinicalInfo";

describe("Encounter", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const vitalData = [
      {
        title: "Vitals",
        value: `Height: 65 inches\n\nWeight: 150 Lbs\n\nBody Mass Index (BMI): 25`,
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
    container = render(
      <ClinicalInfo activeProblemsDetails={[]} vitalData={vitalData} />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
