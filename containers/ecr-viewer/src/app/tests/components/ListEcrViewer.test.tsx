import { fireEvent, render, screen } from "@testing-library/react";
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

describe("Pagination for home page", () => {
  const listFhirData = Array.from({ length: 51 }, (_, i) => ({
    ecrId: `id-${i + 1}`,
    dateModified: `2021-01-0${(i % 9) + 1}`,
  }));
  beforeEach(() => {
    render(<ListECRViewer listFhirData={listFhirData} />);
  });

  it("should render first page correctly", () => {
    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(26); // 25 data rows + 1 header row
  });

  it("should navigate to the next page correctly using the Next button", () => {
    const nextButton = screen.getByTestId("pagination-next");
    fireEvent.click(nextButton);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(26);
    expect(screen.getByText("id-26")).toBeInTheDocument();
    expect(screen.getByText("id-50")).toBeInTheDocument();
  });

  it("should navigate to the previous page correctly using the Previous button", () => {
    const nextButton = screen.getByTestId("pagination-next");
    fireEvent.click(nextButton); // Must navigate past 1st page so Previous button can display

    const previousButton = screen.getByTestId("pagination-previous");
    fireEvent.click(previousButton);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(26);
    expect(screen.getByText("id-1")).toBeInTheDocument();
    expect(screen.getByText("id-25")).toBeInTheDocument();
  });

  it("should navigate to a specific page correctly when clicking page button", () => {
    const page3Button = screen.getByText("3", { selector: "button" });
    fireEvent.click(page3Button);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(2);
    expect(screen.getByText("id-51")).toBeInTheDocument();
  });
});
