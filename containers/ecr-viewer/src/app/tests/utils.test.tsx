import {
  DisplayData,
  evaluateEcrMetadata,
  evaluateSocialData,
  extractPatientAddress,
  calculatePatientAge,
  evaluateClinicalData,
  evaluatePatientName,
  returnProblemsTable,
  returnCareTeamTable,
  isDataAvailable,
  DataDisplay,
} from "@/app/utils";
import { loadYamlConfig } from "@/app/api/utils";
import { Bundle } from "fhir/r4";
import BundleWithTravelHistory from "../tests/assets/BundleTravelHistory.json";
import BundleWithPatient from "../tests/assets/BundlePatient.json";
import BundleWithEcrMetadata from "../tests/assets/BundleEcrMetadata.json";
import BundleWithSexualOrientation from "../tests/assets/BundleSexualOrientation.json";
import BundleWithMiscNotes from "../tests/assets/BundleMiscNotes.json";
import BundleNoActiveProblems from "../tests/assets/BundleNoActiveProblems.json";
import BundleCareTeam from "../tests/assets/BundleCareTeam.json";
import React from "react";
import { render, screen } from "@testing-library/react";
import { evaluate } from "fhirpath";
import userEvent from "@testing-library/user-event";

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
  describe("Evaluate Ecr Metadata", () => {
    it("should have no available data where there is no data", () => {
      const actual = evaluateEcrMetadata(undefined as any, mappings);
      expect(actual.ecrSenderDetails.availableData).toBeEmpty();
      expect(actual.ecrSenderDetails.unavailableData).not.toBeEmpty();

      expect(actual.eicrDetails.availableData).toBeEmpty();
      expect(actual.eicrDetails.unavailableData).not.toBeEmpty();

      expect(actual.rrDetails.availableData).toBeUndefined();
    });
    it("should have ecrSenderDetails", () => {
      const actual = evaluateEcrMetadata(
        BundleWithEcrMetadata as unknown as Bundle,
        mappings,
      );

      expect(actual.ecrSenderDetails.availableData).toEqual([
        { title: "Date/Time eCR Created", value: "07/28/2022 10:01 AM EDT" },
        {
          title: "Sender Facility Name",
          value: "Vanderbilt University Adult Hospital",
        },
        {
          title: "Facility Address",
          value: "1211 Medical Center Dr\nNashville, TN\n37232",
        },
        { title: "Facility Contact", value: "+1-615-322-5000" },
        { title: "Facility ID", value: "1.2.840.114350.1.13.478.3.7.2.686980" },
      ]);
      expect(actual.ecrSenderDetails.unavailableData).toEqual([
        { title: "Sender Software" },
      ]);
    });
    it("should have eicrDetails", () => {
      const actual = evaluateEcrMetadata(
        BundleWithEcrMetadata as unknown as Bundle,
        mappings,
      );

      expect(actual.eicrDetails.availableData).toEqual([
        {
          title: "eICR Identifier",
          value: "1.2.840.114350.1.13.478.3.7.8.688883.230886",
        },
      ]);
      expect(actual.eicrDetails.unavailableData).toBeEmpty();
    });
    it("should have rrDetails", () => {
      const actual = evaluateEcrMetadata(
        BundleWithEcrMetadata as unknown as Bundle,
        mappings,
      );

      expect(actual.rrDetails).toEqual({
        "Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)":
          {
            "COVID-19 (as a diagnosis or active problem)": new Set([
              "Tennessee Department of Health",
            ]),
            "Detection of SARS-CoV-2 nucleic acid in a clinical or post-mortem specimen by any method":
              new Set(["Tennessee Department of Health"]),
          },
      });
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
      const actual = extractPatientAddress(undefined as any, mappings);

      expect(actual).toBeEmpty();
    });
    it("should get patient address", () => {
      const actual = extractPatientAddress(
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

  describe("Extract Patient Address", () => {
    it("should return empty string if no address is available", () => {
      const actual = extractPatientAddress(undefined as any, mappings);

      expect(actual).toBeEmpty();
    });
    it("should get patient address", () => {
      const actual = extractPatientAddress(
        BundleWithPatient as unknown as Bundle,
        mappings,
      );

      expect(actual).toEqual("1050 CARPENTER ST\nEDWARDS, CA\n93523-2800, US");
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
      const input: DisplayData = {};
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item with no length in its value array, it should return false", () => {
      const input: DisplayData = {
        value: [],
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item whose value matches one of the unavailable terms, it should return false", () => {
      const input: DisplayData = {
        value: "Not on file documented in this encounter",
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(false);
    });
    it("given an item with available info, it should return true", () => {
      const input: DisplayData = {
        value: "01/01/1970",
      };
      const result = isDataAvailable(input);
      expect(result).toEqual(true);
    });
  });

  describe("DataDisplay", () => {
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
});
