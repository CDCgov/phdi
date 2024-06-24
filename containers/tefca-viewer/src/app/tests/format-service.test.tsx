import { render } from "@testing-library/react";
import { formatDate, formatAddress, formatName } from "@/app/format-service";
import { Address, HumanName } from "fhir/r4";

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

describe.only("formatName", () => {
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

describe("Format Address", () => {
  it("should return an empty string when given an empty array", () => {
    const address: Address[] = [];
    const { container } = render(formatAddress(address));
    expect(container).toBeEmptyDOMElement();
  });

  it("should handle an address with empty fields gracefully", () => {
    const address: Address[] = [
      {
        line: [""],
        city: "",
        state: "",
        postalCode: "",
      },
    ];
    const { container } = render(formatAddress(address));
    expect(container).toBeEmptyDOMElement();
  });

  it("should format a single address correctly", () => {
    const address: Address[] = [
      {
        line: ["123 Main St"],
        city: "Washington",
        state: "DC",
        postalCode: "20000",
      },
    ];
    const { getByText } = render(formatAddress(address));
    expect(getByText("123 Main St")).toBeInTheDocument();
    expect(getByText("Washington, DC 20000")).toBeInTheDocument();
  });

  it("should format an address with multiple lines correctly", () => {
    const address: Address[] = [
      {
        line: ["123 Main St", "Apt 1"],
        city: "Washington",
        state: "DC",
        postalCode: "20000",
      },
    ];
    const { getByText } = render(formatAddress(address));
    expect(getByText("123 Main St")).toBeInTheDocument();
    expect(getByText("Apt 1")).toBeInTheDocument();
    expect(getByText("Washington, DC 20000")).toBeInTheDocument();
  });

  it("should handle missing line array gracefully", () => {
    const address: Address[] = [
      {
        city: "Washington",
        state: "DC",
        postalCode: "20000",
      },
    ];
    const { getByText } = render(formatAddress(address));
    expect(getByText("Washington, DC 20000")).toBeInTheDocument();
  });

  it("should handle missing city, state, and postalCode gracefully", () => {
    const address: Address[] = [
      {
        line: ["123 Main St"],
      },
    ];
    const { getByText } = render(formatAddress(address));
    expect(getByText("123 Main St")).toBeInTheDocument();
  });
});
