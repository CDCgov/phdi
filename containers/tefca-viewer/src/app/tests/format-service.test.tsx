import { render, screen } from "@testing-library/react";
import {
  formatAddress,
  formatContact,
  formatCodeableConcept,
  formatDate,
  formatIdentifier,
  formatName,
  formatMRN,
  formatString,
} from "@/app/format-service";
import {
  Address,
  HumanName,
  ContactPoint,
  Identifier,
  CodeableConcept,
} from "fhir/r4";

describe("formatDate", () => {
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

describe("formatIdentifier", () => {
  it("should handle fully typed identifiers correctly", () => {
    const identifiers: Identifier[] = [
      {
        value: "999-99-9999",
        type: {
          coding: [
            {
              code: "SSN",
              system: "http://hl7.org/fhir/sid/us-ssn",
              display: "Social Security Number",
            },
          ],
        },
      },
      {
        value: "0123456789",
        type: {
          coding: [
            {
              code: "URI",
              system: "urn:ietf:rfc:3986",
              display: "Internal Reference Identifier",
            },
          ],
        },
      },
    ];

    const { getByText } = render(formatIdentifier(identifiers));
    // Turn off exact matching because the presence of the id_type breaks
    // the value across multiple elements
    expect(getByText("999-99-9999", { exact: false })).toBeInTheDocument();
    expect(
      getByText("Social Security Number", { exact: false }),
    ).toBeInTheDocument();
    expect(getByText("0123456789", { exact: false })).toBeInTheDocument();
    expect(
      getByText("Internal Reference Identifier", { exact: false }),
    ).toBeInTheDocument();
  });

  it("should handle identifiers who lack a coding but have a type", () => {
    const identifiers: Identifier[] = [
      {
        value: "999-99-9999",
        type: {
          text: "us-ssn",
        },
      },
    ];

    const { getByText } = render(formatIdentifier(identifiers));
    // Turn off exact matching because the presence of the id_type breaks
    // the value across multiple elements
    expect(getByText("999-99-9999", { exact: false })).toBeInTheDocument();
    expect(getByText("us-ssn", { exact: false })).toBeInTheDocument();
  });

  it("should handle identifiers who lack both coding and type text", () => {
    const identifiers: Identifier[] = [
      {
        value: "999-99-9999",
      },
    ];

    render(formatIdentifier(identifiers));
    expect(screen.getByText(": 999-99-9999")).toBeInTheDocument();
  });

  it("should handle an empty identifier array without breaking", () => {
    const identifiers: Identifier[] = [];
    const { container } = render(formatIdentifier(identifiers));
    expect(container).toBeEmptyDOMElement();
  });
});

describe("formatString", () => {
  it("should convert all character to lower case", () => {
    const inputString = "TestOfSomeCAPITALS";
    const expectedString = "testofsomecapitals";
    const result = formatString(inputString);
    expect(result).toEqual(expectedString);
  });

  it("should also replace all spaces with underscores", () => {
    const inputString = "JoHn ShEpArD";
    const expectedString = "john-shepard";
    const result = formatString(inputString);
    expect(result).toEqual(expectedString);
  });

  it("should remove all non alpha-numeric characters", () => {
    const inputString = "*C0MPL3X_$TR!NG*";
    const expectedString = "c0mpl3xtrng";
    const result = formatString(inputString);
    expect(result).toEqual(expectedString);
  });
});

describe("formatAddress", () => {
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

describe("formatContact", () => {
  it("should format phone contact correctly", () => {
    const contacts: ContactPoint[] = [
      {
        system: "phone",
        value: "123-456-7890",
        use: "home",
      },
    ];

    const { getByText } = render(formatContact(contacts));
    expect(getByText("home: 123-456-7890")).toBeInTheDocument();
  });

  it("should format email contact correctly", () => {
    const contacts: ContactPoint[] = [
      {
        system: "email",
        value: "test@example.com",
      },
    ];

    const { getByText } = render(formatContact(contacts));
    expect(getByText("test@example.com")).toBeInTheDocument();
  });

  it("should handle mixed contact types correctly", () => {
    const contacts: ContactPoint[] = [
      {
        system: "phone",
        value: "123-456-7890",
        use: "home",
      },
      {
        system: "email",
        value: "test@example.com",
      },
    ];

    const { getByText } = render(formatContact(contacts));
    expect(getByText(/home:\s123-456-7890/)).toBeInTheDocument();
    expect(getByText(/test@example.com/)).toBeInTheDocument();
  });

  it("should return null for unsupported contact system", () => {
    const contacts: ContactPoint[] = [
      {
        system: "idk",
        value: "it was on the form",
      },
    ];

    const { container } = render(formatContact(contacts));
    expect(container).toBeEmptyDOMElement();
  });

  it("should handle empty contact array gracefully", () => {
    const contacts: ContactPoint[] = [];

    const { container } = render(formatContact(contacts));
    expect(container).toBeEmptyDOMElement();
  });
});

describe("formatCodeableConcept", () => {
  it("should return an empty string when concept is undefined", () => {
    const result = formatCodeableConcept(undefined);
    expect(result).toBe("");
  });

  it("should return the text property when coding is not defined", () => {
    const concept: CodeableConcept = {
      text: "Example Text",
    };

    const { getByText } = render(formatCodeableConcept(concept));
    expect(getByText("Example Text")).toBeInTheDocument();
  });

  it("should return the text property when coding array is empty", () => {
    const concept: CodeableConcept = {
      text: "Example Text",
      coding: [],
    };

    const { getByText } = render(formatCodeableConcept(concept));
    expect(getByText("Example Text")).toBeInTheDocument();
  });

  it("should return the display, code, and system of the first coding object", () => {
    const concept: CodeableConcept = {
      text: "Example Text",
      coding: [
        {
          display: "Example Display",
          code: "Example Code",
          system: "Example System",
        },
      ],
    };

    const { getByText } = render(formatCodeableConcept(concept));
    expect(getByText(/Example Display/)).toBeInTheDocument();
    expect(getByText(/Example Code/)).toBeInTheDocument();
    expect(getByText(/Example System/)).toBeInTheDocument();
  });
});
