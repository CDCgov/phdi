import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import ClinicalInfo from "@/app/view-data/components/ClinicalInfo";

describe("Clinical Info", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const clinicalNotes = [
      {
        title: "Clinical Notes",
        value: "<paragraph>This patient was only recently discharged for a recurrent GI bleed as described</paragraph>",
      }
    ];
    container = render(
      <ClinicalInfo
        clinicalNotes={clinicalNotes}
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