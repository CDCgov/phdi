import { render } from "@testing-library/react";
import { formatDate, formatName, formatMRN } from "@/app/format-service";
import { HumanName, Identifier } from "fhir/r4";

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

describe("formatName", () => {
  it("should format a single HumanName correctly", () => {
    const names: HumanName[] = [
      {
        family: "Doe",
        given: ["John"],
      },
    ];
    const result = formatName(names);
    expect(result).toBe("John Doe");
  });

  it("should handle multiple given names correctly", () => {
    const names: HumanName[] = [
      {
        family: "Smith",
        given: ["Jane", "Alice"],
      },
    ];
    const result = formatName(names);
    expect(result).toBe("Jane Alice Smith");
  });

  it("should return an empty string if family name is missing", () => {
    const names: HumanName[] = [
      {
        given: ["John"],
      },
    ];
    const result = formatName(names);
    expect(result).toBe("John");
  });

  it("should return an empty string if given names are missing", () => {
    const names: HumanName[] = [
      {
        family: "Doe",
      },
    ];
    const result = formatName(names);
    expect(result).toBe("Doe");
  });

  it("should handle missing given and family names gracefully", () => {
    const names: HumanName[] = [
      {
        family: undefined,
        given: [""],
      },
    ];
    const result = formatName(names);
    expect(result).toBe("");
  });
});

describe("formatMRN", () => {
  it("should render the MRN value correctly", () => {
    const identifiers: Identifier[] = [
      {
        value: "12345",
        type: {
          coding: [
            {
              code: "MR",
            },
          ],
        },
      },
    ];

    const { getByText } = render(formatMRN(identifiers));
    expect(getByText("12345")).toBeInTheDocument();
  });

  it("should return null if no MRN is present", () => {
    const identifiers: Identifier[] = [
      {
        value: "67890",
        type: {
          coding: [
            {
              code: "notMR",
            },
          ],
        },
      },
    ];

    const { container } = render(formatMRN(identifiers));
    expect(container).toBeEmptyDOMElement();
  });

  it("should handle empty identifier array gracefully", () => {
    const identifiers: Identifier[] = [];

    const { container } = render(formatMRN(identifiers));
    expect(container).toBeEmptyDOMElement();
  });
});
