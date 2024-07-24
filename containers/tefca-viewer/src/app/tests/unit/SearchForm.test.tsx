import { FormatPhoneAsDigits } from "@/app/query/components/SearchForm";

describe("FormatPhoneAsDigits", () => {
  it("should handle dashes, spacecs, and dot delimiters", () => {
    const dashInput = "123-456-7890";
    const expectedResult = "1234567890";
    expect(FormatPhoneAsDigits(dashInput)).toEqual(expectedResult);

    const spaceInput = "123 456 7890";
    expect(FormatPhoneAsDigits(spaceInput)).toEqual(expectedResult);

    const dotInput = "123.456.7890";
    expect(FormatPhoneAsDigits(dotInput)).toEqual(expectedResult);
  });
  it("should handle parentheticals around area codes", () => {
    const expectedResult = "1234567890";
    let parentheticalInput = "(123) 456 7890";
    expect(FormatPhoneAsDigits(parentheticalInput)).toEqual(expectedResult);

    parentheticalInput = "(123)456-7890";
    expect(FormatPhoneAsDigits(parentheticalInput)).toEqual(expectedResult);
  });
  it("should handle extraneous white spaces regardless of position", () => {
    const expectedResult = "1234567890";
    const weirdSpaceNumber = "  123  - 456 7 8 9 0  ";
    expect(FormatPhoneAsDigits(weirdSpaceNumber)).toEqual(expectedResult);
  });
  it("should gracefully fail if provided a partial number", () => {
    const givenPhone = "456-7890";
    const expectedResult = "456-7890";
    expect(FormatPhoneAsDigits(givenPhone)).toEqual(expectedResult);
  });
  it("should gracefully fail if given a country code", () => {
    const givenPhone = "+44 202 555 8736";
    const expectedResult = "+44 202 555 8736";
    expect(FormatPhoneAsDigits(givenPhone)).toEqual(expectedResult);
  });
});
