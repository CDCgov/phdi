import { axe } from "jest-axe";
import { render } from "@testing-library/react";
import EcrTable from "@/app/components/EcrTable";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";

jest.mock("../../api/services/listEcrDataService");

describe("EcrTable", () => {
  const mockedListEcrData = jest.mocked(listEcrData);
  const mockData: EcrDisplay[] = Array.from({ length: 51 }, (_, i) => ({
    ecrId: `id-${i + 1}`,
    patient_first_name: `first-${i + 1}`,
    patient_last_name: `last-${i + 1}`,
    dateModified: `2021-01-0${(i % 9) + 1}`,
    patient_date_of_birth: `2000-01-0${(i % 9) + 1}`,
    reportable_condition: `reportable-condition-${i + 1}`,
    rule_summary: `rule-summary-${i + 1}`,
    patient_report_date: `2021-01-0${(i % 9) + 1}`,
    date_created: `2021-01-0${(i % 9) + 1}`,
  }));

  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("should match snapshot", async () => {
    mockedListEcrData.mockResolvedValue(mockData);
    const { container } = render(
      await EcrTable({ currentPage: 1, itemsPerPage: 25 }),
    );
    expect(container).toMatchSnapshot();
  });

  it("should pass accessibility", async () => {
    mockedListEcrData.mockResolvedValue(mockData);
    const { container } = render(
      await EcrTable({ currentPage: 1, itemsPerPage: 25 }),
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
