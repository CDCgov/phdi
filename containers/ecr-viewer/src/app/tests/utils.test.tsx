import { isDataAvailable } from "@/app/utils";
import { loadYamlConfig } from "@/app/api/services/utils";
import { Bundle } from "fhir/r4";
import BundleWithTravelHistory from "./assets/BundleTravelHistory.json";
import BundleWithPatient from "./assets/BundlePatient.json";
import BundleWithSexualOrientation from "./assets/BundleSexualOrientation.json";
import BundleWithMiscNotes from "./assets/BundleMiscNotes.json";
import BundleNoActiveProblems from "./assets/BundleNoActiveProblems.json";
import BundleCareTeam from "./assets/BundleCareTeam.json";
import React from "react";
import { render, screen } from "@testing-library/react";
import { CarePlanActivity } from "fhir/r4b";
import { evaluate } from "@/app/view-data/utils/evaluate";
import userEvent from "@testing-library/user-event";
import { Tooltip } from "@trussworks/react-uswds";
import {
  evaluateSocialData,
  evaluatePatientName,
  calculatePatientAge,
  evaluatePatientAddress,
} from "../services/evaluateFhirDataService";
import {
  evaluateClinicalData,
  returnCareTeamTable,
  returnPlannedProceduresTable,
  returnProblemsTable,
} from "../view-data/components/common";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";
import { TooltipDiv, ToolTipElement } from "@/app/ToolTipElement";

describe("Utils", () => {
  const mappings = loadYamlConfig();
  describe("Evaluate Social Data", () => {
    it("should have no available data when there is no data", () => {
      const actual = evaluateSocialData(undefined as any, mappings);

      expect(actual.availableData).toBeEmpty();
      expect(actual.unavailableData).not.toBeEmpty();
    });
    it("should have travel history when there is a travel history observation present", () => {
      const actual = evaluateSocialData(
        BundleWithTravelHistory as unknown as Bundle,
        mappings,
      );

      expect(actual.availableData[0].value)
        .toEqualIgnoringWhitespace(`Dates: 2018-01-18 - 2018-02-18
           Location(s): Traveled to Singapore, Malaysia and Bali with my family.
           Purpose of Travel: Active duty military (occupation)`);
    });
    it("should have patient sexual orientation when available", () => {
      const actual = evaluateSocialData(
        BundleWithSexualOrientation as unknown as Bundle,
        mappings,
      );

      expect(actual.availableData[0].value).toEqual("Other");
    });
  });

  describe("Evaluate Clinical Info", () => {
    it("Should return notes", () => {
      const actual = evaluateClinicalData(
        BundleWithMiscNotes as unknown as Bundle,
        mappings,
      );
      render(actual.clinicalNotes.availableData[0].value as React.JSX.Element);
      expect(actual.clinicalNotes.availableData[0].title).toEqual(
        "Miscellaneous Notes",
      );
      expect(screen.getByText("Active Problems")).toBeInTheDocument();
      expect(actual.clinicalNotes.unavailableData).toBeEmpty();
    });
  });

  describe("Evaluate Care Team Table", () => {
    it("should evaluate care team table results", () => {
      const actual: React.JSX.Element = returnCareTeamTable(
        BundleCareTeam as unknown as Bundle,
        mappings,
      ) as React.JSX.Element;

      render(actual);

      expect(screen.getByText("Dr. Gregory House")).toBeInTheDocument();
      expect(screen.getByText("family")).toBeInTheDocument();
      expect(
        screen.getByText("Start: 11/16/2004 End: 05/21/2012"),
      ).toBeInTheDocument();
    });

    it("the table should not appear when there are no results", () => {
      const actual = returnCareTeamTable(
        BundleWithPatient as unknown as Bundle,
        mappings,
      );
      expect(actual).toBeUndefined();
    });
  });

  describe("Evaluate Patient Name", () => {
    it("should return name", () => {
      const actual = evaluatePatientName(
        BundleWithPatient as unknown as Bundle,
        mappings,
      );
      expect(actual).toEqual("ABEL CASTILLO");
    });
  });
  describe("Extract Patient Address", () => {
    it("should return empty string if no address is available", () => {
      const actual = evaluatePatientAddress(undefined as any, mappings);

      expect(actual).toBeEmpty();
    });
    it("should get patient address", () => {
      const actual = evaluatePatientAddress(
        BundleWithPatient as unknown as Bundle,
        mappings,
      );

      expect(actual).toEqual("1050 CARPENTER ST\nEDWARDS, CA\n93523-2800, US");
    });
  });
  describe("Calculate Patient Age", () => {
    it("when no date is given, should return patient age when DOB is available", () => {
      // Fixed "today" for testing purposes
      jest.useFakeTimers().setSystemTime(new Date("2024-03-12"));

      const patientAge = calculatePatientAge(
        BundleWithPatient as unknown as Bundle,
        mappings,
      );

      expect(patientAge).toEqual(8);

      // Return to real time
      jest.useRealTimers();
    });
    it("should return nothing when DOB is unavailable", () => {
      const patientAge = calculatePatientAge(undefined as any, mappings);

      expect(patientAge).toEqual(undefined);
    });
    it("when date is given, should return age at given date", () => {
      const givenDate = "2020-01-01";
      const expectedAge = 4;

      const resultAge = calculatePatientAge(
        BundleWithPatient as unknown as Bundle,
        mappings,
        givenDate,
      );

      expect(resultAge).toEqual(expectedAge);
    });
  });

  describe("Planned Procedures Table", () => {
    it("should return table when data is provided", () => {
      const carePlanActivities = [
        {
          detail: {
            scheduledString: "02/01/2024",
            code: {
              coding: [
                {
                  display: "activity 1",
                },
              ],
            },
          },
          extension: [
            {
              url: "dibbs.orderedDate",
              valueString: "01/01/2024",
            },
          ],
        },
      ] as CarePlanActivity[];
      const actual = returnPlannedProceduresTable(carePlanActivities, mappings);
      render(actual!);

      expect(screen.getByText("activity 1")).toBeInTheDocument();
      expect(screen.getByText("01/01/2024")).toBeInTheDocument();
      expect(screen.getByText("02/01/2024")).toBeInTheDocument();
    });
    it("should not return table when data is provided", () => {
      const actual = returnPlannedProceduresTable([], mappings);

      expect(actual).toBeUndefined();
    });
  });

  describe("Render Active Problem table", () => {
    it("should return empty if active problem name is undefined", () => {
      const actual = returnProblemsTable(
        BundleNoActiveProblems as unknown as Bundle,
        evaluate(BundleNoActiveProblems, mappings["activeProblems"]),
        mappings,
      );

      expect(actual).toBeUndefined();
    });
  });

  describe("isDataAvailable", () => {
    it("given an item with no value, it should return false", () => {
      const input: DisplayDataProps = {};
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item with no length in its value array, it should return false", () => {
      const input: DisplayDataProps = {
        value: [],
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item whose value matches one of the unavailable terms, it should return false", () => {
      const input: DisplayDataProps = {
        value: "Not on file documented in this encounter",
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item with available info, it should return true", () => {
      const input: DisplayDataProps = {
        value: "01/01/1970",
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(true);
    });
  });

  describe("DataDisplay", () => {
    describe("string value", () => {
      it("should display text up to 500 characters", () => {
        const FiveHundredChars =
          "xVP5yPfQAbNOFOOl8Vi1ytfcQ39Cz0dl73SBMj6xQHuCwRRO1FmS7v5wqD55U914tsDfqTtsEQ0mISsLoiMZbco4iwb2xU3nNL6YAneY0tMqsJdb55JWHSI2uqyuuwIvjjZY5Jl9vIda6lLoYke3ywsQFR6nlEFCipJMF9vA9OQqkZljCYirZJu4kZTENk6V1Yirwuzw9L6uV3avK6VhMK6o8qZbxLkDFnMgjzx8kf25tz98mU5m6Rp8zNcY2cf02xA2aV27WfeWvy5TS73SzJK8a9cFZxCe5xsHtAkVqNa4UzGINwt6i2mLN4kuGgmk7GZGoMaOcNyaOr80TfgpWVjqLMobAXvjv1JHBXLXHczFG8jKQtU3U3FoAxTu39CPcjuq43BWsNej1inbzexa7e9njXZUvZGa3z5Nep4vlrQQtV8F5jZFGHvdlhLr1ZdRJE8sAQEi9nWHviYHSYCVR1ijVNtcHVj9JKkJZ5FAn1a9hDFVq2Tz";
        expect(FiveHundredChars).toHaveLength(500);

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredChars }} />,
        );

        expect(screen.getByText(FiveHundredChars)).toBeInTheDocument();
      });
      it("should only show first 300 characters when full string is greater than 500 characters", () => {
        const FiveHundredOneChars =
          "xVP5yPfQAbNOFOOl8Vi1ytfcQ39Cz0dl73SBMj6xQHuCwRRO1FmS7v5wqD55U914tsDfqTtsEQ0mISsLoiMZbco4iwb2xU3nNL6YAneY0tMqsJdb55JWHSI2uqyuuwIvjjZY5Jl9vIda6lLoYke3ywsQFR6nlEFCipJMF9vA9OQqkZljCYirZJu4kZTENk6V1Yirwuzw9L6uV3avK6VhMK6o8qZbxLkDFnMgjzx8kf25tz98mU5m6Rp8zNcY2cf02xA2aV27WfeWvy5TS73SzJK8a9cFZxCe5xsHtAkVqNa4UzGINwt6i2mLN4kuGgmk7GZGoMaOcNyaOr80TfgpWVjqLMobAXvjv1JHBXLXHczFG8jKQtU3U3FoAxTu39CPcjuq43BWsNej1inbzexa7e9njXZUvZGa3z5Nep4vlrQQtV8F5jZFGHvdlhLr1ZdRJE8sAQEi9nWHviYHSYCVR1ijVNtcHVj9JKkJZ5FAn1a9hDFVq2Tz1";
        expect(FiveHundredOneChars).toHaveLength(501);

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredOneChars }} />,
        );

        expect(
          screen.getByText(FiveHundredOneChars.substring(0, 300) + "..."),
        ).toBeInTheDocument();
        expect(screen.getByText("View more")).toBeInTheDocument();
        expect(
          screen.queryByText(FiveHundredOneChars.substring(300)),
        ).not.toBeInTheDocument();
      });
      it("should show full text when view more is clicked", async () => {
        const user = userEvent.setup();
        const FiveHundredOneChars =
          "xVP5yPfQAbNOFOOl8Vi1ytfcQ39Cz0dl73SBMj6xQHuCwRRO1FmS7v5wqD55U914tsDfqTtsEQ0mISsLoiMZbco4iwb2xU3nNL6YAneY0tMqsJdb55JWHSI2uqyuuwIvjjZY5Jl9vIda6lLoYke3ywsQFR6nlEFCipJMF9vA9OQqkZljCYirZJu4kZTENk6V1Yirwuzw9L6uV3avK6VhMK6o8qZbxLkDFnMgjzx8kf25tz98mU5m6Rp8zNcY2cf02xA2aV27WfeWvy5TS73SzJK8a9cFZxCe5xsHtAkVqNa4UzGINwt6i2mLN4kuGgmk7GZGoMaOcNyaOr80TfgpWVjqLMobAXvjv1JHBXLXHczFG8jKQtU3U3FoAxTu39CPcjuq43BWsNej1inbzexa7e9njXZUvZGa3z5Nep4vlrQQtV8F5jZFGHvdlhLr1ZdRJE8sAQEi9nWHviYHSYCVR1ijVNtcHVj9JKkJZ5FAn1a9hDFVq2Tz1";
        expect(FiveHundredOneChars).toHaveLength(501);

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredOneChars }} />,
        );

        await user.click(screen.getByText("View more"));

        expect(screen.getByText(FiveHundredOneChars)).toBeInTheDocument();
        expect(screen.getByText("View less")).toBeInTheDocument();
        expect(screen.queryByText("View more")).not.toBeInTheDocument();
        expect(screen.queryByText("...")).not.toBeInTheDocument();
      });
      it("should hide text when view less is clicked", async () => {
        const user = userEvent.setup();
        const FiveHundredOneChars =
          "xVP5yPfQAbNOFOOl8Vi1ytfcQ39Cz0dl73SBMj6xQHuCwRRO1FmS7v5wqD55U914tsDfqTtsEQ0mISsLoiMZbco4iwb2xU3nNL6YAneY0tMqsJdb55JWHSI2uqyuuwIvjjZY5Jl9vIda6lLoYke3ywsQFR6nlEFCipJMF9vA9OQqkZljCYirZJu4kZTENk6V1Yirwuzw9L6uV3avK6VhMK6o8qZbxLkDFnMgjzx8kf25tz98mU5m6Rp8zNcY2cf02xA2aV27WfeWvy5TS73SzJK8a9cFZxCe5xsHtAkVqNa4UzGINwt6i2mLN4kuGgmk7GZGoMaOcNyaOr80TfgpWVjqLMobAXvjv1JHBXLXHczFG8jKQtU3U3FoAxTu39CPcjuq43BWsNej1inbzexa7e9njXZUvZGa3z5Nep4vlrQQtV8F5jZFGHvdlhLr1ZdRJE8sAQEi9nWHviYHSYCVR1ijVNtcHVj9JKkJZ5FAn1a9hDFVq2Tz1";
        expect(FiveHundredOneChars).toHaveLength(501);

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredOneChars }} />,
        );

        await user.click(screen.getByText("View more"));
        expect(screen.getByText(FiveHundredOneChars)).toBeInTheDocument();

        await user.click(screen.getByText("View less"));

        expect(
          screen.getByText(FiveHundredOneChars.substring(0, 300) + "..."),
        ).toBeInTheDocument();
        expect(screen.getByText("View more")).toBeInTheDocument();
        expect(
          screen.queryByText(FiveHundredOneChars.substring(300)),
        ).not.toBeInTheDocument();
      });
    });
    describe("Array ReactNode value", () => {
      it("should only show first 300 characters when the full element contains greater than 500 characters", () => {
        const OneHundredTwentyFiveCharStrings = [
          "gFuhsHGaiecclYWTrp7EvwBAr2JAhfN9Kv09RtBbj4QevWU1FolfXZJBWPgW6LCTUaDaiYMiHDOhNXrIeqn1ICE7fBHTRY1Gq8f5f9g9oAyCKwf2uluoe8nDzXJmV",
          "pHW6mej26PNCPI1GRAkq7ForT93tNROGU4D4FE8fJETXar1hLVCZXGSQRZBDwBOtXCK0jT7LxtNedMAt4RxLFsM23KpFpvx7ke3EfOOBBOeyulFcXqZaonYkObOv9",
          "KCu7m7fYs5Jw2IeNf9PtmVHmNJakfdwu19783oUXwHcm9gUAMnQ5FQEgnsfCLy1r79Fx4hQhLm8rdz4sA4cMMD6r8Cpsgt9KsImZRNH2RC5BRgb6cMsGAfOTb8Kri",
          "qWF7VqoRKetCfdzvRupMCtFNrwZBJb2NEReYStddzm4GGOADg6m5nhgC0goXgzB3GKVIp6qY60aOmyjPnyH2OrAZszdmnthkh6DwI4VROKwPTKbGJorQTy3B8oi8p",
          "C35z0HsExV59WKHHsBgupEXcHnxyp4rtlfmhWA067Go52PJvzeNgoKU4h27JWobzjWAQ6U9WdEboVvFkkp2SpSkUzG0YR38Ijl3vYpfumtJMFBLvFkPrEkjEbo7UF",
        ];
        const FiveHundredOneChars = [
          <ul key={"1234"}>
            <li>{OneHundredTwentyFiveCharStrings[0]}</li>
            <li>{OneHundredTwentyFiveCharStrings[1]}</li>
            <li>{OneHundredTwentyFiveCharStrings[2]}</li>
            <li>{OneHundredTwentyFiveCharStrings[3]}</li>
            <li>{OneHundredTwentyFiveCharStrings[4]}</li>
          </ul>,
          "this is more text",
        ];

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredOneChars }} />,
        );

        expect(
          screen.getByText(OneHundredTwentyFiveCharStrings[0]),
        ).toBeInTheDocument();
        expect(
          screen.getByText(OneHundredTwentyFiveCharStrings[1]),
        ).toBeInTheDocument();
        expect(
          screen.getByText(
            OneHundredTwentyFiveCharStrings[2].substring(0, 50) + "...",
          ),
        ).toBeInTheDocument();
        expect(screen.getByText("View more")).toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[2].substring(50)),
        ).not.toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[3]),
        ).not.toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[4]),
        ).not.toBeInTheDocument();
      });
      it("should show the whole ReactNode when view more is clicked", async () => {
        const user = userEvent.setup();
        const OneHundredTwentyFiveCharStrings = [
          "gFuhsHGaiecclYWTrp7EvwBAr2JAhfN9Kv09RtBbj4QevWU1FolfXZJBWPgW6LCTUaDaiYMiHDOhNXrIeqn1ICE7fBHTRY1Gq8f5f9g9oAyCKwf2uluoe8nDzXJmV",
          "pHW6mej26PNCPI1GRAkq7ForT93tNROGU4D4FE8fJETXar1hLVCZXGSQRZBDwBOtXCK0jT7LxtNedMAt4RxLFsM23KpFpvx7ke3EfOOBBOeyulFcXqZaonYkObOv9",
          "KCu7m7fYs5Jw2IeNf9PtmVHmNJakfdwu19783oUXwHcm9gUAMnQ5FQEgnsfCLy1r79Fx4hQhLm8rdz4sA4cMMD6r8Cpsgt9KsImZRNH2RC5BRgb6cMsGAfOTb8Kri",
          "qWF7VqoRKetCfdzvRupMCtFNrwZBJb2NEReYStddzm4GGOADg6m5nhgC0goXgzB3GKVIp6qY60aOmyjPnyH2OrAZszdmnthkh6DwI4VROKwPTKbGJorQTy3B8oi8p",
          "C35z0HsExV59WKHHsBgupEXcHnxyp4rtlfmhWA067Go52PJvzeNgoKU4h27JWobzjWAQ6U9WdEboVvFkkp2SpSkUzG0YR38Ijl3vYpfumtJMFBLvFkPrEkjEbo7UF",
        ];
        const LongReactNode = [
          <ul key={"1234"}>
            <li>{OneHundredTwentyFiveCharStrings[0]}</li>
            <li>{OneHundredTwentyFiveCharStrings[1]}</li>
            <li>{OneHundredTwentyFiveCharStrings[2]}</li>
            <li>{OneHundredTwentyFiveCharStrings[3]}</li>
            <li>{OneHundredTwentyFiveCharStrings[4]}</li>
          </ul>,
          "this is more text",
        ];

        render(<DataDisplay item={{ title: "field", value: LongReactNode }} />);

        await user.click(screen.getByText("View more"));

        OneHundredTwentyFiveCharStrings.forEach((str) =>
          expect(screen.getByText(str)).toBeInTheDocument(),
        );
        expect(screen.getByText("this is more text")).toBeInTheDocument();
        expect(screen.getByText("View less")).toBeInTheDocument();
      });
      it("should only show first 300 characters when ReactNode element when view less is clicked", async () => {
        const user = userEvent.setup();
        const OneHundredTwentyFiveCharStrings = [
          "gFuhsHGaiecclYWTrp7EvwBAr2JAhfN9Kv09RtBbj4QevWU1FolfXZJBWPgW6LCTUaDaiYMiHDOhNXrIeqn1ICE7fBHTRY1Gq8f5f9g9oAyCKwf2uluoe8nDzXJmV",
          "pHW6mej26PNCPI1GRAkq7ForT93tNROGU4D4FE8fJETXar1hLVCZXGSQRZBDwBOtXCK0jT7LxtNedMAt4RxLFsM23KpFpvx7ke3EfOOBBOeyulFcXqZaonYkObOv9",
          "KCu7m7fYs5Jw2IeNf9PtmVHmNJakfdwu19783oUXwHcm9gUAMnQ5FQEgnsfCLy1r79Fx4hQhLm8rdz4sA4cMMD6r8Cpsgt9KsImZRNH2RC5BRgb6cMsGAfOTb8Kri",
          "qWF7VqoRKetCfdzvRupMCtFNrwZBJb2NEReYStddzm4GGOADg6m5nhgC0goXgzB3GKVIp6qY60aOmyjPnyH2OrAZszdmnthkh6DwI4VROKwPTKbGJorQTy3B8oi8p",
          "C35z0HsExV59WKHHsBgupEXcHnxyp4rtlfmhWA067Go52PJvzeNgoKU4h27JWobzjWAQ6U9WdEboVvFkkp2SpSkUzG0YR38Ijl3vYpfumtJMFBLvFkPrEkjEbo7UF",
        ];
        const FiveHundredOneChars = [
          <ul key={"1234"}>
            <li>{OneHundredTwentyFiveCharStrings[0]}</li>
            <li>{OneHundredTwentyFiveCharStrings[1]}</li>
            <li>{OneHundredTwentyFiveCharStrings[2]}</li>
            <li>{OneHundredTwentyFiveCharStrings[3]}</li>
            <li>{OneHundredTwentyFiveCharStrings[4]}</li>
          </ul>,
          "this is more text",
        ];

        render(
          <DataDisplay item={{ title: "field", value: FiveHundredOneChars }} />,
        );
        await user.click(screen.getByText("View more"));
        await user.click(screen.getByText("View less"));

        expect(
          screen.getByText(OneHundredTwentyFiveCharStrings[0]),
        ).toBeInTheDocument();
        expect(
          screen.getByText(OneHundredTwentyFiveCharStrings[1]),
        ).toBeInTheDocument();
        expect(
          screen.getByText(
            OneHundredTwentyFiveCharStrings[2].substring(0, 50) + "...",
          ),
        ).toBeInTheDocument();
        expect(screen.getByText("View more")).toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[2].substring(50)),
        ).not.toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[3]),
        ).not.toBeInTheDocument();
        expect(
          screen.queryByText(OneHundredTwentyFiveCharStrings[4]),
        ).not.toBeInTheDocument();
      });
    });
  });

  describe("ToolTips", () => {
    it("should return the tool tip with the custom jsx", () => {
      render(
        <Tooltip
          label={"test label"}
          asCustom={TooltipDiv}
          className="testClass"
        >
          Test child
        </Tooltip>,
      );
      const tip = screen.getByTestId("triggerElement");
      expect(tip.className).toInclude("testClass");
      expect(tip.textContent).toInclude("Test child");
    });
    it("should make a tooltip", () => {
      render(<ToolTipElement content={"Item Title"} toolTip={"Tooltip"} />);
      const tip = screen.getByTestId("triggerElement");
      expect(tip.className).toInclude("short-tooltip");
      expect(tip.textContent).toInclude("Item Title");
    });
    it("should not make the tool tip short if the tip has more than 100 character", () => {
      const toolTip =
        "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890";
      render(<ToolTipElement content={"Item Title"} toolTip={toolTip} />);
      const tip = screen.getByTestId("triggerElement");
      expect(tip.className).not.toInclude("short-tooltip");
    });
  });
});
