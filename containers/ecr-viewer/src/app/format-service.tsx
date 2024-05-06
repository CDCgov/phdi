import React from "react";
import { toolTipElement } from "@/app/utils";

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

/**
 * Formats an address based on its components.
 * @param streetAddress - An array containing street address lines.
 * @param city - The city name.
 * @param state - The state or region name.
 * @param zipCode - The ZIP code or postal code.
 * @param country - The country name.
 * @returns The formatted address string.
 */
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
 * Format a datetime string to "MM/DD/YYYY HH:MM AM/PM Z" where "Z" is the timezone abbreviation.If
 * the input string contains a UTC offset then the returned string will be in the format
 * "MM/DD/YYYY HH:MM AM/PM ±HH:MM". If the input string do not contain a time part, the returned
 * string will be in the format "MM/DD/YYYY". If the input string is not in the expected format, it
 * will be returned as is. If the input is falsy a blank string will be returned. The following
 * formats are supported:
 * - "YYYY-MM-DDTHH:MM±HH:MM"
 * - "YYYY-MM-DDTHH:MMZ"
 * - "YYYY-MM-DD"
 * - "MM/DD/YYYY HH:MM AM/PM ±HH:MM"
 * @param dateTimeString datetime string.
 * @returns Formatted datetime string.
 */
export const formatDateTime = (dateTimeString: string): string => {
  if (!dateTimeString) {
    return "";
  }

  // This is roughly the format that we want to convert to, therefore we can return it as is.
  const customFormatRegex = /^\d{2}\/\d{2}\/\d{4} \d\d?:\d{2} [AP]M \w{3}$/;
  const isoDateTimeRegex =
    /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?)?/;
  if (customFormatRegex.test(dateTimeString)) {
    return dateTimeString;
  } else if (isoDateTimeRegex.test(dateTimeString)) {
    // Split the datetime string into date and time parts
    const [datePart, timePart] = dateTimeString.split("T");

    // Further split the date part into YYYY, MM, DD
    const [year, month, day] = datePart.split("-");

    if (timePart) {
      // Split the time part into HH:MM:SS and timezone (±HH:MM)
      const [time, timeZone] = timePart.split(/(?=[+-])/);

      // We only need HH:MM from the time
      const [hours, minutes] = time.split(":");

      // Convert 24-hour time to 12-hour time
      const hoursInt = parseInt(hours, 10);
      const suffix = hoursInt >= 12 ? "PM" : "AM";
      const hours12 = ((hoursInt + 11) % 12) + 1; // Convert 24h to 12h format

      const formattedDateTime = `${month}/${day}/${year} ${hours12}:${minutes} ${suffix} ${timeZone || "UTC"}`;
      return formattedDateTime;
    }

    // Reformat the string as needed
    const formattedDate = `${month}/${day}/${year}`;
    return formattedDate;
  }

  // If the input string is not in the expected format, return it as is
  return dateTimeString;
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
      const formattedDate = `${dateString.substring(
        0,
        4,
      )}-${dateString.substring(4, 6)}-${dateString.substring(6, 8)}`; // yyyy-mm-dd
      date = new Date(formattedDate);
    }
    // double check that the reformat actually worked otherwise return nothing
    if (date.toString() != "Invalid Date") {
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        timeZone: "UTC",
      }); // UTC, otherwise will have timezone issues
    }
  }
};

/**
 * Formats a phone number into a standard format of XXX-XXX-XXXX.
 * @param phoneNumber - The phone number to format.
 * @returns The formatted phone number or undefined if the input is invalid.
 */
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

/**
 * Formats vital signs information into a single line string with proper units .
 * @param heightAmount - The amount of height.
 * @param heightUnit - The measurement type of height (e.g., "[in_i]" for inches, "cm" for centimeters).
 * @param weightAmount - The amount of weight.
 * @param weightUnit - The measurement type of weight (e.g., "[lb_av]" for pounds, "kg" for kilograms).
 * @param bmi - The Body Mass Index (BMI).
 * @returns The formatted vital signs information.
 */
export const formatVitals = (
  heightAmount: string,
  heightUnit: string,
  weightAmount: string,
  weightUnit: string,
  bmi: string,
) => {
  let heightString = "";
  let weightString = "";
  let bmiString = "";

  let heightType = "";
  let weightType = "";
  if (heightAmount && heightUnit) {
    if (heightUnit === "[in_i]") {
      heightType = "inches";
    } else if (heightUnit === "cm") {
      heightType = "cm";
    }
    heightString = `Height: ${heightAmount} ${heightType}\n\n`;
  }

  if (weightAmount && weightUnit) {
    if (weightUnit === "[lb_av]") {
      weightType = "Lbs";
    } else if (weightUnit === "kg") {
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

/**
 * Formats a string by converting it to lowercase, replacing spaces with underscores, and removing special characters except underscores.
 * @param input - The input string to be formatted.
 * @returns The formatted string.
 */
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

/**
 * Adds a caption to a table element.
 * @param element - The React element representing the table.
 * @param caption - The caption text to be added.
 * @param toolTip - Tooltip for caption
 * @returns A React element with the caption added as the first child of the table.
 */
export const addCaptionToTable = (
  element: React.ReactNode,
  caption: string,
  toolTip?: string,
) => {
  if (React.isValidElement(element) && element.type === "table") {
    return React.cloneElement(element, {}, [
      <caption key="caption">
        <div className="data-title">{toolTipElement(caption, toolTip)}</div>
      </caption>,
      ...React.Children.toArray(element.props.children),
    ]);
  }

  return element;
};

/**
 * Removes HTML tags from a given string.
 * @param element - The input string containing HTML elements.
 * @returns - A string with all HTML tags removed.
 */
export const removeHtmlElements = (element: string): string => {
  const regex = /<[^>]*>/g;
  return element.replace(regex, "");
};
