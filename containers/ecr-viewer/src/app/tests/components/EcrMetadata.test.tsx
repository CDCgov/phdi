import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrMetadata from "../../view-data/components/EcrMetadata";
import React from "react";
import { DisplayDataProps } from "@/app/view-data/components/DataDisplay";
import {
  ERSDWarning,
  ReportableConditions,
} from "@/app/services/ecrMetadataService";

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
      {
        title: "Date/Time eCR Created",
        value: "2022-05-14T12:56:38Z",
      },
      { title: "eICR Release Version", value: "R1.1 (2016-12-01)" },
      {
        title: "EHR Software Name",
        value: "Epic - Version 10.1",
      },
      { title: "EHR Manufacturer Model Name", value: "Epic - Version 10.1" },
    ];

    const eRSDwarnings: ERSDWarning[] = [
      {
        warning:
          "Sending organization is using an malformed eRSD (RCTC) version",
        versionUsed: "2020-06-23",
        expectedVersion:
          "Sending organization should be using one of the following: 2023-10-06, 1.2.2.0, 3.x.x.x.",
        suggestedSolution:
          "The trigger code version your organization is using could not be determined. The trigger codes may be out date. Please have your EHR administrators update the version format for complete eCR functioning.",
      },
    ];

    container = render(
      <EcrMetadata
        eicrDetails={eicrDetails}
        rrDetails={rrConditionsList}
        eRSDwarnings={eRSDwarnings}
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
