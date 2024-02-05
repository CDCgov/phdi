import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import Clinical from "@/app/view-data/components/Clinical";

describe("Clinical", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const clinicalNotes = [
      {
        title: "Miscellaneous Notes",
        value: "<paragraph>This patient was only recently discharged for a recurrent GI bleed as described</paragraph>",
      }
    ];
    const activeProblemsDetails = [{
      title: "blah",
      value: <table
        className="usa-table usa-table--borderless width-full border-top border-left border-right table-caption-margin"
        data-testid="table">
        <caption>Problems List</caption>
        <thead>
        <tr>
          <th scope="col" className=" bg-gray-5 minw-15">Active Problem</th>
          <th scope="col" className=" bg-gray-5 minw-15">Onset Age</th>
          <th scope="col" className=" bg-gray-5 minw-15">Onset Date</th>
        </tr>
        </thead>
        <tbody>
        <tr>
          <th scope="row" className="text-top">Coronavirus infection</th>
          <td className="text-top">N/A</td>
          <td className="text-top">09/28/2022</td>
        </tr>
        <tr>
          <th scope="row" className="text-top">Close exposure to COVID-19 virus</th>
          <td className="text-top">N/A</td>
          <td className="text-top">09/28/2022</td>
        </tr>
        <tr>
          <th scope="row" className="text-top">Seasonal allergies</th>
          <td className="text-top">N/A</td>
          <td className="text-top">09/24/2022</td>
        </tr>
        </tbody>
      </table>
    }];
    container = render(
      <Clinical
        activeProblemsDetails={activeProblemsDetails}
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