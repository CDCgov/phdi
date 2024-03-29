import {
  formatDate,
  extractNumbersAndPeriods,
  formatTablesToJSON,
} from "@/app/format-service";

describe("Format Date", () => {
  it("should return the correct formatted date", () => {
    const inputDate = "2023-01-15";
    const expectedDate = "01/15/2023";

    const result = formatDate(inputDate);
    expect(result).toEqual(expectedDate);
  });

  it("should return N/A if provided date is an empty string", () => {
    const inputDate = "";

    const result = formatDate(inputDate);
    expect(result).toBeUndefined();
  });

  it("should return N/A if provided date is undefined", () => {
    const inputDate = undefined;

    const result = formatDate(inputDate as any);
    expect(result).toBeUndefined();
  });

  it("should return N/A if provided date is null", () => {
    const inputDate = null;

    const result = formatDate(inputDate as any);
    expect(result).toBeUndefined();
  });
});

describe("formatTablesToJSON", () => {
  it("should return the JSON object given an HTML string", () => {
    const htmlString =
      "<li data-id='Result.12345'><table><thead><tr><th>Component</th><th>Analysis Time</th></tr></thead><tbody><tr data-id='Result.12345.Comp1'><td data-id='Result.12345.Comp1Name'>Campylobacter, NAAT</td><td>01/01/2024 1:00 PM PDT</td></tr><tr data-id='Result.12345.Comp2'><td data-id='Result.12345.Comp2Name'>Salmonella, NAAT</td><td>01/01/2024 1:00 PM PDT</td></tr></tbody></table><table><thead><tr><th>Specimen (Source)</th><th>Collection Time</th><th>Received Time</th></tr></thead><tbody><tr><td data-id='Result.12345.Specimen'>Stool</td><td>01/01/2024 12:00 PM PDT</td><td>01/01/2024 12:00 PM PDT</td></tr></tbody></table></li>";
    const expectedResult = [
      {
        resultId: "Result.12345",
        resultName:
          "ComponentAnalysis TimeCampylobacter, NAAT01/01/2024 1:00 PM PDTSalmonella, NAAT01/01/2024 1:00 PM PDTSpecimen (Source)Collection TimeReceived TimeStool01/01/2024 12:00 PM PDT01/01/2024 12:00 PM PDT",
        tables: [
          [
            {
              Component: {
                value: "Campylobacter, NAAT",
                metadata: {
                  "data-id": "Result.12345.Comp1Name",
                },
              },
              "Analysis Time": {
                value: "01/01/2024 1:00 PM PDT",
                metadata: {},
              },
            },
            {
              Component: {
                value: "Salmonella, NAAT",
                metadata: {
                  "data-id": "Result.12345.Comp2Name",
                },
              },
              "Analysis Time": {
                value: "01/01/2024 1:00 PM PDT",
                metadata: {},
              },
            },
          ],
          [
            {
              "Specimen (Source)": {
                value: "Stool",
                metadata: {
                  "data-id": "Result.12345.Specimen",
                },
              },
              "Collection Time": {
                value: "01/01/2024 12:00 PM PDT",
                metadata: {},
              },
              "Received Time": {
                value: "01/01/2024 12:00 PM PDT",
                metadata: {},
              },
            },
          ],
        ],
      },
    ];

    const result = formatTablesToJSON(htmlString);

    expect(result).toEqual(expectedResult);
  });

  it("should return an empty array when HTML string input has no tables", () => {
    const htmlString =
      "<div><h1>Hello, World!</h1><p>This HTML string has no tables.</p></div>";
    const expectedResult = [];

    const result = formatTablesToJSON(htmlString);

    expect(result).toEqual(expectedResult);
  });
});

describe("extractNumbersAndPeriods", () => {
  it("should return the correctly formatted sequence of numbers and periods", () => {
    const inputArray = [
      "#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp2",
      "#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670844.Comp3",
    ];
    const expectedResult = [
      "1.2.840.114350.1.13.297.3.7.2.798268.1670845",
      "1.2.840.114350.1.13.297.3.7.2.798268.1670844",
    ];

    const result = extractNumbersAndPeriods(inputArray);
    expect(result).toEqual(expectedResult);
  });

  it("should return an empty string if no periods are found", () => {
    const inputArray = ["foo", "bar"];
    const expectedResult = ["", ""];

    const result = extractNumbersAndPeriods(inputArray);
    expect(result).toEqual(expectedResult);
  });

  it("should return an empty string if only one period is found", () => {
    const inputArray = ["foo.bar", "hello.there"];
    const expectedResult = ["", ""];

    const result = extractNumbersAndPeriods(inputArray);
    expect(result).toEqual(expectedResult);
  });
});
