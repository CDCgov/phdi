import { fireEvent, render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import ListECRViewer from "@/app/ListEcrViewer";

describe("Home Page, ListECRViewer", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const listData = [
      {
        ecrId: "12345",
        date_created: "04/16/2024 9:40 PM UTC",
        patient_first_name: "John",
        patient_last_name: "Doe",
        patient_date_of_birth: "01/01/1970",
        patient_report_date: "04/16/2024 9:40 PM UTC",
        reportable_condition: "COVID-19",
        rule_summary: "Positive",
      },
      {
        ecrId: "23456",
        date_created: "04/16/2024 9:41 PM UTC",
        patient_first_name: "Jane",
        patient_last_name: "Doe",
        patient_date_of_birth: "02/01/1955",
        patient_report_date: "04/16/2024 9:40 PM UTC",
        reportable_condition: "COVID-19",
        rule_summary: "Positive",
      },
      {
        ecrId: "34567",
        date_created: "04/16/2024 9:42 PM UTC",
        patient_first_name: "Dan",
        patient_last_name: "Doe",
        patient_date_of_birth: "12/01/1984",
        patient_report_date: "04/16/2024 9:40 PM UTC",
        reportable_condition: "COVID-19",
        rule_summary: "Positive",
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
    patient_first_name: `first-${i + 1}`,
    patient_last_name: `last-${i + 1}`,
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
    expect(screen.getByText("first-26 last-26")).toBeInTheDocument();
    expect(screen.getByText("first-50 last-50")).toBeInTheDocument();
  });

  it("should navigate to the previous page correctly using the Previous button", () => {
    const nextButton = screen.getByTestId("pagination-next");
    fireEvent.click(nextButton); // Must navigate past 1st page so Previous button can display

    const previousButton = screen.getByTestId("pagination-previous");
    fireEvent.click(previousButton);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(26);
    expect(screen.getByText("first-1 last-1")).toBeInTheDocument();
    expect(screen.getByText("first-25 last-25")).toBeInTheDocument();
  });

  it("should navigate to a specific page correctly when clicking page button", () => {
    const page3Button = screen.getByText("3", { selector: "button" });
    fireEvent.click(page3Button);

    const rows = screen.getAllByRole("row");
    expect(rows).toHaveLength(2);
    expect(screen.getByText("first-51 last-51")).toBeInTheDocument();
  });
});
