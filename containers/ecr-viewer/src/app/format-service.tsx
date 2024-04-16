interface Metadata {
  [key: string]: string;
}

export interface TableRow {
  [key: string]: {
    value: any;
    metadata: Metadata;
  };
}

export interface TableJson {
  resultId?: string;
  resultName?: string;
  tables?: TableRow[][];
}

export interface TableJson {
  resultId?: string;
  resultName?: string;
  tables?: TableRow[][];
}

/**
 * Formats a person's name using given name(s), family name, optional prefix(es), and optional suffix(es).
 * @param given - Optional array of given name(s).
 * @param family - Optional string representing family name or surname.
 * @param [prefix] - Optional array of name prefix(es).
 * @param [suffix] - Optional array of name suffix(es).
 * @returns Formatted name.
 */
export const formatName = (
  given?: string[],
  family?: string,
  prefix?: string[],
  suffix?: string[],
) => {
  const nameArray: string[] = [];
  if (prefix) {
    nameArray.push(...prefix);
  }
  if (given) {
    nameArray.push(...given);
  }
  if (family) {
    nameArray.push(family);
  }
  if (suffix) {
    nameArray.push(...suffix);
  }

  return nameArray.join(" ").trim();
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

/**
 * Formats the given date and time string according to the specified options.
 * If the time is included in the input string, it formats the date and time in the local time zone
 * with the year, month, day, and time components. Otherwise, it formats only the date with the
 * year, month, and day components in the UTC time zone.
 * @param dateTime - The date and time string to be formatted.
 * @returns The formatted date and time string.
 */
export const formatDateTime = (dateTime: string) => {
  const hasTime = dateTime?.includes(":");
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    timeZoneName: hasTime ? "short" : undefined,
  };
  if (hasTime) {
    options.hour = "numeric";
    options.minute = "2-digit";
  } else {
    options.timeZone = "UTC"; // UTC, otherwise will have timezone issues
  }
  const date = new Date(dateTime)
    .toLocaleDateString("en-Us", options)
    .replace(",", "");
  return date !== "Invalid Date" ? date : "";
};

/**
 * Formats the provided date string into a formatted date string with year, month, and day.
 * @param dateString - The date string to be formatted. formatDate will also be able to take 'yyyymmdd' as input
 * @returns - The formatted date string, "Invalid Date" if input date was invalid, or undefined if the input date is falsy.
 */

export const formatDate = (dateString?: string): string | undefined => {
  if (dateString) {
    let date = new Date(dateString);
    if (date.toString() == "Invalid Date") {
      const formattedDate = `${dateString.substring(0, 4)}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`; // yyyy-mm-dd
      date = new Date(formattedDate);
    }
    return date.toLocaleDateString("en-US", {
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
      .replace("+1", "")
      .replace(/\D/g, "")
      .replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  } catch {
    return undefined;
  }
};

/**
 * Formats the provided start and end date-time strings and returns a formatted string
 * with both the start and end times. Each time is labeled and separated by a carriage return
 * and newline for clarity in display or further processing.
 * @param startDateTime - The start date-time string to be formatted.
 * @param endDateTime - The end date-time string to be formatted.
 * @returns A string with the formatted start and end times, each on a new line.
 */
export const formatStartEndDateTime = (
  startDateTime: string,
  endDateTime: string,
) => {
  const textArray: String[] = [];

  const startDateObject = formatDateTime(startDateTime);
  const endDateObject = formatDateTime(endDateTime);

  if (startDateObject) {
    textArray.push(`Start: ${startDateObject}`);
  }
  if (endDateObject) {
    textArray.push(`End: ${endDateObject}`);
  }

  return textArray.join("\n");
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

/**
 * Parses an HTML string containing tables or a list of tables and converts each table into a JSON array of objects.
 * Each <li> item represents a different lab result. The resulting JSON objects contain the data-id (Result ID)
 * and text content of the <li> items, along with an array of JSON representations of the tables contained within each <li> item.
 * @param htmlString - The HTML string containing tables to be parsed.
 * @returns - An array of JSON objects representing the list items and their tables from the HTML string.
 * @example @returns [{resultId: 'Result.123', resultName: 'foo', tables: [{}, {},...]}, ...]
 */
export function formatTablesToJSON(htmlString: string): TableJson[] {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, "text/html");
  const jsonArray: any[] = [];
  const liArray = doc.querySelectorAll("li");
  if (liArray.length > 0) {
    liArray.forEach((li) => {
      const tables: any[] = [];
      const resultId = li.getAttribute("data-id");
      const resultName = li.childNodes[0].textContent?.trim() ?? "";
      li.querySelectorAll("table").forEach((table) => {
        tables.push(processTable(table));
      });
      jsonArray.push({ resultId, resultName, tables });
    });
  } else {
    doc.querySelectorAll("table").forEach((table) => {
      const resultName = table.caption?.textContent;
      const resultId = table.getAttribute("data-id") ?? undefined;
      jsonArray.push({ resultId, resultName, tables: [processTable(table)] });
    });
  }

  return jsonArray;
}

/**
 * Processes a single HTML table element, extracting data from rows and cells, and converts it into a JSON array of objects.
 * This function extracts data from <tr> and <td> elements within the provided table element.
 * The content of <th> elements is used as keys in the generated JSON objects.
 * @param table - The HTML table element to be processed.
 * @returns - An array of JSON objects representing the rows and cells of the table.
 */
function processTable(table: Element): TableRow[] {
  const jsonArray: any[] = [];
  const rows = table.querySelectorAll("tr");
  const keys: string[] = [];

  rows[0].querySelectorAll("th").forEach((header) => {
    keys.push(header.textContent?.trim() ?? "");
  });

  rows.forEach((row, rowIndex) => {
    // Skip the first row as it contains headers
    if (rowIndex === 0) return;

    const obj: TableRow = {};
    row.querySelectorAll("td").forEach((cell, cellIndex) => {
      const key = keys[cellIndex];

      const metaData: Metadata = {};
      const attributes = cell.attributes || [];
      for (const element of attributes) {
        const attrName = element.nodeName;
        const attrValue = element.nodeValue;
        if (attrName && attrValue) {
          metaData[attrName] = attrValue;
        }
      }
      obj[key] = {
        value: cell.textContent?.trim() ?? "",
        metadata: metaData,
      };
    });
    jsonArray.push(obj);
  });

  return jsonArray;
}

/**
 * Extracts and concatenates all sequences of numbers and periods from each string in the input array,
 * excluding any leading and trailing periods in the first matched sequence of each string.
 * @param inputValues - An array of strings from which numbers and periods will be extracted.
 * @returns An array of strings, each corresponding to an input string with all found sequences
 * of numbers and periods concatenated together, with any leading period in the first sequence removed.
 * @example @param inputValues - ['#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp2']
 * @example @returns - ['1.2.840.114350.1.13.297.3.7.2.798268.1670845']
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

/**
 * Truncates up to the character limit. If it stops in the middle of the word, it removes the whole word.
 * @param input_str - The string to truncate
 * @param character_limit - The number of characters to truncate defaults to 30
 * @returns - The string that was
 */
export const truncateLabNameWholeWord = (
  input_str: string,
  character_limit: number = 30,
) => {
  if (input_str.length <= character_limit) {
    return input_str;
  }

  const trimStr = input_str.substring(0, 30);
  const lastSpaceIndex = trimStr.lastIndexOf(" ");

  if (lastSpaceIndex === -1) {
    return input_str.length <= character_limit ? input_str : "";
  }

  // Truncate to the last full word within the limit
  return input_str.substring(0, lastSpaceIndex);
};

/**
 * Converts a string to sentence case, making the first character uppercase and the rest lowercase.
 * @param str - The string to convert to sentence case.
 * @returns The converted sentence-case string. If the input is empty or not a string, the original input is returned.
 */
export function toSentenceCase(str: string) {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}
