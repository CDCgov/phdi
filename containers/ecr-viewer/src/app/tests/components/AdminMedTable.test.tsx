import { AdministeredMedication } from "@/app/view-data/components/AdministeredMedication";
import { render, screen } from "@testing-library/react";

describe("AdminMedTable", () => {
  it("should not render anything if there is no administered medications", () => {
    render(<AdministeredMedication medicationData={[]} />);

    expect(
      screen.queryByText("Administered Medications"),
    ).not.toBeInTheDocument();
  });

  it("should render administered medications", () => {
    render(
      <AdministeredMedication
        medicationData={[{ name: "aspirin tablet 325 mg", date: "09/29/2022" }]}
      />,
    );

    expect(screen.getByText("Administered Medications")).toBeVisible();
    expect(screen.getByText("aspirin tablet 325 mg")).toBeVisible();
    expect(screen.getByText("09/29/2022")).toBeVisible();
  });
});
