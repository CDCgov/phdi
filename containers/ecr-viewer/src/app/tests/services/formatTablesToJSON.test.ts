import { formatTablesToJSON } from "@/app/services/formatTablesToJSON";

describe("formatTablesToJSON", () => {
  it("should return the JSON object given an HTML string", () => {
    const htmlString =
      "<li data-id='Result.12345'>Lab Test<table><thead><tr><th>Component</th><th>Analysis Time</th></tr></thead><tbody><tr data-id='Result.12345.Comp1'><td data-id='Result.12345.Comp1Name'>Campylobacter, NAAT</td><td>01/01/2024 1:00 PM PDT</td></tr><tr data-id='Result.12345.Comp2'><td data-id='Result.12345.Comp2Name'>Salmonella, NAAT</td><td>01/01/2024 1:00 PM PDT</td></tr></tbody></table><table><thead><tr><th>Specimen (Source)</th><th>Collection Time</th><th>Received Time</th></tr></thead><tbody><tr><td data-id='Result.12345.Specimen'>Stool</td><td>01/01/2024 12:00 PM PDT</td><td>01/01/2024 12:00 PM PDT</td></tr></tbody></table></li>";
    const expectedResult = [
      {
        resultId: "Result.12345",
        resultName: "Lab Test",
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
    const expectedResult: [] = [];

    const result = formatTablesToJSON(htmlString);

    expect(result).toEqual(expectedResult);
  });

  it("should return the JSON object given a table html string", () => {
    const tableString =
      "<table><caption>Pending Results</caption><thead><tr><th>Name</th></tr></thead><tbody><tr data-id='procedure9'><td>test1</td></tr></tbody></table><table><caption>Scheduled Orders</caption></caption><thead><tr><th>Name</th></tr></thead><tbody><tr data-id='procedure10'><td>test2</td></tr></tbody></table>documented as of this encounter\n";
    const expectedResult = [
      {
        resultName: "Pending Results",
        tables: [[{ Name: { metadata: {}, value: "test1" } }]],
      },
      {
        resultName: "Scheduled Orders",
        tables: [[{ Name: { metadata: {}, value: "test2" } }]],
      },
    ];
    const result = formatTablesToJSON(tableString);

    expect(result).toEqual(expectedResult);
  });
});
