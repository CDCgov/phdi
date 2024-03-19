interface MetaData {
  [key: string]: string;
}

export const formatName = (firstName: string, lastName: string) => {
  if (firstName != undefined) {
    return `${firstName} ${lastName}`.trim();
  } else {
    return undefined;
  }
};

export const formatAddress = (
  streetAddress: string[],
  city: string,
  state: string,
  zipCode: string,
  country: string,
) => {
  let address = {
    streetAddress: streetAddress || [],
    cityState: [city, state],
    zipCodeCountry: [zipCode, country],
  };

  return [
    address.streetAddress.join("\n"),
    address.cityState.filter(Boolean).join(", "),
    address.zipCodeCountry.filter(Boolean).join(", "),
  ]
    .filter(Boolean)
    .join("\n");
};

export const formatDateTime = (dateTime: string) => {
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "numeric",
    minute: "2-digit",
  };

  return new Date(dateTime)
    .toLocaleDateString("en-Us", options)
    .replace(",", "");
};

/**
 * Formats the provided date string into a formatted date string with year, month, and day.
 * @param {string} date - The date string to be formatted.
 * @returns {string | undefined} - The formatted date string or undefined if the input date is falsy.
 */
export const formatDate = (date?: string): string | undefined => {
  if (date) {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      timeZone: "UTC",
    }); // UTC, otherwise will have timezone issues
  }
};

export const formatPhoneNumber = (phoneNumber: string) => {
  try {
    return phoneNumber
      .replace(/\D/g, "")
      .replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  } catch {
    return undefined;
  }
};

export const formatStartEndDateTime = (
  startDateTime: "string",
  endDateTime: "string",
) => {
  const startDateObject = new Date(startDateTime);
  const endDateObject = new Date(endDateTime);

  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  };

  const startFormattedDate = startDateObject
    .toLocaleString("en-US", options)
    .replace(",", "");
  const endFormattedDate = endDateObject
    .toLocaleString("en-us", options)
    .replace(",", "");

  return `Start: ${startFormattedDate}
        End: ${endFormattedDate}`;
};

export const formatVitals = (
  heightAmount: string,
  heightMeasurementType: string,
  weightAmount: string,
  weightMeasurementType: string,
  bmi: string,
) => {
  let heightString = "";
  let weightString = "";
  let bmiString = "";

  let heightType = "";
  let weightType = "";
  if (heightAmount && heightMeasurementType) {
    if (heightMeasurementType === "[in_i]") {
      heightType = "inches";
    } else if (heightMeasurementType === "cm") {
      heightType = "cm";
    }
    heightString = `Height: ${heightAmount} ${heightType}\n\n`;
  }

  if (weightAmount && weightMeasurementType) {
    if (weightMeasurementType === "[lb_av]") {
      weightType = "Lbs";
    } else if (weightMeasurementType === "kg") {
      weightType = "kg";
    }
    weightString = `Weight: ${weightAmount} ${weightType}\n\n`;
  }

  if (bmi) {
    bmiString = `Body Mass Index (BMI): ${bmi}`;
  }

  const combinedString = `${heightString} ${weightString} ${bmiString}`;
  return combinedString.trim();
};

export const formatString = (input: string): string => {
  // Convert to lowercase
  let result = input.toLowerCase();

  // Replace spaces with underscores
  result = result.replace(/\s+/g, "-");

  // Remove all special characters except underscores
  result = result.replace(/[^a-z0-9\-]/g, "");

  return result;
};

export function formatTablesToJSON(htmlString: string): any[] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, "text/html");
  const jsonArray: any[] = [];
  doc.querySelectorAll("table").forEach((table) => {
    jsonArray.push(processTable(table));
  });

  return jsonArray;
}

function processTable(table: Element): any[] {
  const jsonArray: any[] = [];
  const rows = table.querySelectorAll("tr");
  const keys: string[] = [];

  rows[0].querySelectorAll("th").forEach((header) => {
    keys.push(header.textContent?.trim() || "");
  });

  rows.forEach((row, rowIndex) => {
    // Skip the first row as it contains headers
    if (rowIndex === 0) return;

    const obj: { [key: string]: string } = {};
    row.querySelectorAll("td").forEach((cell, cellIndex) => {
      const key = keys[cellIndex];

      const metaData: MetaData = {};
      const attributes = cell.attributes || [];
      for (let i = 0; i < attributes.length; i++) {
        const attrName = attributes[i].nodeName;
        const attrValue = attributes[i].nodeValue;
        metaData[attrName] = attrValue;
      }
      obj[key] = {
        value: cell.textContent?.trim() || "",
        metadata: metaData,
      };
    });
    jsonArray.push(obj);
  });

  return jsonArray;
}

/**
 * Extracts and concatenates all sequences of numbers and periods from each string in the input array,
 * excluding any leading period in the first matched sequence of each string.
 *
 * @param {string[]} inputValues - An array of strings from which numbers and periods will be extracted.
 * @returns {string[]} An array of strings, each corresponding to an input string with all found sequences
 * of numbers and periods concatenated together, with any leading period in the first sequence removed.
 */
export function extractNumbersAndPeriods(inputValues: string[]): string[] {
  return inputValues.map((value) => {
    // Find all sequences of numbers and periods up to the first occurrence of a letter
    const pattern: RegExp = /[0-9.]+(?=[a-zA-Z])/;
    const match: RegExpMatchArray | null = value.match(pattern);

    if (match && match[0]) {
      // Remove leading and trailing periods from the match
      const cleanedMatch = match[0].replace(/^\./, "").replace(/\.$/, "");
      return cleanedMatch;
    }
    return "";
  });
}
