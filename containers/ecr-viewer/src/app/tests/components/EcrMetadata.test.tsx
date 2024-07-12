import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrMetadata from "../../view-data/components/EcrMetadata";
import React from "react";
import { DisplayDataProps } from "@/app/DataDisplay";
import { ReportableConditions } from "@/app/services/ecrMetadataService";

describe("ECR Metadata", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const mockChildMethod = jest.fn();
    jest.spyOn(React, "useRef").mockReturnValue({
      current: {
        childMethod: mockChildMethod,
      },
    });
    const rrConditionsList: ReportableConditions = {
      "Disease caused by severe acute respiratory syndrome coronavirus 2(disorder)":
        {
          "Detection of SARS-CoV-2 nucleic acid in a clinical or post-mortem specimen by any method":
            new Set([
              "California Department of Public Health",
              "Los Angeles County Department of Public Health",
            ]),
          "Close contact in the 14 days prior to onset of symptoms with a confirmed or probable case of COVID-19 (Partially implemented as exposure with no timeframe parameters)":
            new Set(["Los Angeles County Department of Public Health"]),
          "COVID-19 (as a diagnosis or active problem)": new Set([
            "Los Angeles County Department of Public Health",
          ]),
        },
    };
    const eicrDetails: DisplayDataProps[] = [
      {
        title: "eICR Identifier",
        value: "1dd10047-2207-4eac-a993-0f706c88be5d",
      },
    ];
    const ecrSenderDetails: DisplayDataProps[] = [
      {
        title: "Date/Time eCR Created",
        value: "2022-05-14T12:56:38Z",
      },
      {
        title: "Sender Software",
        value: "",
      },
      {
        title: "Sender Facility Name",
        value: "PRM- Palmdale Regional Medical Center",
      },
      {
        title: "Facility Address",
        value: "38600 Medical Center Drive\nPalmdale, CA\n93551, USA",
      },
      {
        title: "Facility Contact",
        value: "(661)382-5000",
      },
      {
        title: "Facility ID",
        value: "2.16.840.1.113883.4.6",
      },
    ];

    container = render(
      <EcrMetadata
        eicrDetails={eicrDetails}
        eCRSenderDetails={ecrSenderDetails}
        rrDetails={rrConditionsList}
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
