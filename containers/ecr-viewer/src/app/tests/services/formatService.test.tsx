import {
  formatName,
  formatDate,
  extractNumbersAndPeriods,
  truncateLabNameWholeWord,
  toSentenceCase,
  removeHtmlElements,
  formatDateTime,
} from "@/app/services/formatService";

describe("Format Name", () => {
  const inputGiven = ["Gregory", "B"];
  const inputFamily = "House";

  it("should return only given and family name", () => {
    const expectedName = "Gregory B House";

    const result = formatName(inputGiven, inputFamily);
    expect(result).toEqual(expectedName);
  });

  it("should return the prefix, given, family, and suffix names", () => {
    const inputPrefix = ["Dr."];
    const inputSuffix = ["III"];
    const expectedName = "Dr. Gregory B House III";

    const result = formatName(
      inputGiven,
      inputFamily,
      inputPrefix,
      inputSuffix,
    );
    expect(result).toEqual(expectedName);
  });

  it("should return an empty string", () => {
    const inputEmpty: any[] = [];
    const expectedName = "";

    const result = formatName(inputEmpty, "", inputEmpty, inputEmpty);
    expect(result).toEqual(expectedName);
  });
});

describe("formatDateTime", () => {
  it("Given an ISO date time string, should return the correct formatted date and time", () => {
    const inputDate = "2022-10-11T19:29:00Z";
    const expectedDate = "10/11/2022 7:29 PM UTC";

    const result = formatDateTime(inputDate);
    expect(result).toEqual(expectedDate);
  });

  it("Given an ISO date time string with a UTC offset, should return the correct formatted date and time", () => {
    const inputDate = "2022-12-23T14:59:44-08:00";
    const expectedDate = "12/23/2022 2:59 PM -08:00";

    const result = formatDateTime(inputDate);
    expect(result).toEqual(expectedDate);
  });

  it("Given an ISO date string, should return the correct formatted date", () => {
    const inputDate = "2022-10-11";
    const expectedDate = "10/11/2022";

    const result = formatDateTime(inputDate);
    expect(result).toEqual(expectedDate);
  });

  it("Given a date time in the format of 'MM/DD/YYYY HH:MM AM/PM Z.' (as found in Lab Info Analysis Time), should return the correct formatted date", () => {
    const inputDate = "10/19/2022 10:00 AM PDT";
    const expectedDate = "10/19/2022 10:00 AM PDT";

    const result = formatDateTime(inputDate);
    expect(result).toEqual(expectedDate);
  });
});

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

  it("when given yyyymmdd, should return the correct formatted date", () => {
    const inputDate = "20220125";
    const expectedDate = "01/25/2022";

    const result = formatDate(inputDate);
    expect(result).toEqual(expectedDate);
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

describe("truncateLabNameWholeWord", () => {
  it("should return the original string if it is less than or equal to the character limit", () => {
    const input = "Short string";
    const output = truncateLabNameWholeWord(input, 30);
    expect(output).toBe(input);
  });

  it("should truncate a string to the nearest whole word within the character limit", () => {
    const input = "HOAG MEMORIAL HOSPITAL NEWPORT BEACH LABORATORY";
    const expected = "HOAG MEMORIAL HOSPITAL";
    const output = truncateLabNameWholeWord(input, 30);
    expect(output).toBe(expected);
  });

  it("should return an empty string if the first word is longer than the character limit", () => {
    const input = "Supercalifragilisticexpialidocious";
    const output = truncateLabNameWholeWord(input, 30);
    expect(output).toBe("");
  });

  it("should handle strings exactly at the character limit without truncation", () => {
    const input = "HOAG MEMORIAL HOSPITAL NEWPORT";
    const output = truncateLabNameWholeWord(input, 30);
    expect(output).toBe(input);
  });
});

describe("toSentenceCase", () => {
  it("should return string in sentence case", () => {
    const input = "hello there";
    const expected = "Hello there";

    const result = toSentenceCase(input);
    expect(result).toEqual(expected);
  });
});

describe("removeHtmlElements", () => {
  it("should remove all HTML tags from string", () => {
    const input = "<div><p>Hello <br/>there</p></div>";
    const expected = "Hello there";

    const result = removeHtmlElements(input);
    expect(result).toEqual(expected);
  });
  it("should return the same string if no HTML tags are included", () => {
    const input = "Hello there";
    const expected = "Hello there";

    const result = removeHtmlElements(input);
    expect(result).toEqual(expected);
  });
});
