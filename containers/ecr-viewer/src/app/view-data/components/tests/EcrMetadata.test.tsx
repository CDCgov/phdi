import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrMetadata from "../EcrMetadata";
import { DisplayData } from "@/app/utils";

describe("ECR Metadata", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const rrDetails: DisplayData[] = [
      {
        title: "Reportable Condition(s)",
        value: "Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)"
      },      {
        title: "RCKMS Trigger Summary",
        value: "COVID-19 (as a diagnosis or active problem)"
      },      {
        title: "Jurisdiction(s) Sent eCR",
        value: "California Department of Public Health"
      },
    ];

    const eicrDetails: DisplayData[] = [
      {
        title: "eICR Identifier",
        value: "1dd10047-2207-4eac-a993-0f706c88be5d"
      },
    ];
    const ecrSenderDetails: DisplayData[] = [
      {
        title: "Date/Time eCR Created",
        value: "2022-05-14T12:56:38Z"
      },    {
        title: "Sender Software",
        value: ""
      },    {
        title: "Sender Facility Name",
        value: "PRM- Palmdale Regional Medical Center"
      },    {
        title: "Facility Address",
        value: "38600 Medical Center Drive\nPalmdale, CA\n93551, USA"
      },    {
        title: "Facility Contact",
        value: "(661)382-5000"
      },    {
        title: "Facility ID",
        value: "2.16.840.1.113883.4.6"
      },
    ];

    container = render(
      <EcrMetadata
        eicrDetails={eicrDetails}
        eCRSenderDetails={ecrSenderDetails}
        rrDetails={rrDetails}
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
