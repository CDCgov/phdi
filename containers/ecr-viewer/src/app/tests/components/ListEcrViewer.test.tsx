import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import ListECRViewer from "@/app/ListEcrViewer";

describe("Home Page, ListECRViewer", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const listData = [
      {
        ecrId: "12345",
        dateModified: "04/16/2024 9:40 PM UTC",
      },
      {
        ecrId: "23456",
        dateModified: "04/16/2024 9:41 PM UTC",
      },
      {
        ecrId: "34567",
        dateModified: "04/16/2024 9:42 PM UTC",
      },
    ];
    container = render(<ListECRViewer listFhirData={listData} />).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
