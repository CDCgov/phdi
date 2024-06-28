import React from "react";
export interface Metadata {
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
export declare const formatName: (
  given?: string[],
  family?: string,
  prefix?: string[],
  suffix?: string[],
) => string;
/**
 * Formats an address based on its components.
 * @param streetAddress - An array containing street address lines.
 * @param city - The city name.
 * @param state - The state or region name.
 * @param zipCode - The ZIP code or postal code.
 * @param country - The country name.
 * @returns The formatted address string.
 */
export declare const formatAddress: (
  streetAddress: string[],
  city: string,
  state: string,
  zipCode: string,
  country: string,
) => string;
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
export declare const formatDateTime: (dateTimeString: string) => string;
/**
 * Formats the provided date string into a formatted date string with year, month, and day.
 * @param dateString - The date string to be formatted. formatDate will also be able to take 'yyyymmdd' as input
 * @returns - The formatted date string, "Invalid Date" if input date was invalid, or undefined if the input date is falsy.
 */
export declare const formatDate: (dateString?: string) => string | undefined;
/**
 * Formats a phone number into a standard format of XXX-XXX-XXXX.
 * @param phoneNumber - The phone number to format.
 * @returns The formatted phone number or undefined if the input is invalid.
 */
export declare const formatPhoneNumber: (
  phoneNumber: string,
) => string | undefined;
/**
 * Formats the provided start and end date-time strings and returns a formatted string
 * with both the start and end times. Each time is labeled and separated by a carriage return
 * and newline for clarity in display or further processing.
 * @param startDateTime - The start date-time string to be formatted.
 * @param endDateTime - The end date-time string to be formatted.
 * @returns A string with the formatted start and end times, each on a new line.
 */
export declare const formatStartEndDateTime: (
  startDateTime: string,
  endDateTime: string,
) => string;
/**
 * Formats vital signs information into a single line string with proper units .
 * @param heightAmount - The amount of height.
 * @param heightUnit - The measurement type of height (e.g., "[in_i]" for inches, "cm" for centimeters).
 * @param weightAmount - The amount of weight.
 * @param weightUnit - The measurement type of weight (e.g., "[lb_av]" for pounds, "kg" for kilograms).
 * @param bmi - The Body Mass Index (BMI).
 * @returns The formatted vital signs information.
 */
export declare const formatVitals: (
  heightAmount: string,
  heightUnit: string,
  weightAmount: string,
  weightUnit: string,
  bmi: string,
) => string;
/**
 * Formats a string by converting it to lowercase, replacing spaces with underscores, and removing special characters except underscores.
 * @param input - The input string to be formatted.
 * @returns The formatted string.
 */
export declare const formatString: (input: string) => string;
/**
 * Parses an HTML string containing tables or a list of tables and converts each table into a JSON array of objects.
 * Each <li> item represents a different lab result. The resulting JSON objects contain the data-id (Result ID)
 * and text content of the <li> items, along with an array of JSON representations of the tables contained within each <li> item.
 * @param htmlString - The HTML string containing tables to be parsed.
 * @returns - An array of JSON objects representing the list items and their tables from the HTML string.
 * @example @returns [{resultId: 'Result.123', resultName: 'foo', tables: [{}, {},...]}, ...]
 */
export declare function formatTablesToJSON(htmlString: string): TableJson[];
/**
 * Extracts and concatenates all sequences of numbers and periods from each string in the input array,
 * excluding any leading and trailing periods in the first matched sequence of each string.
 * @param inputValues - An array of strings from which numbers and periods will be extracted.
 * @returns An array of strings, each corresponding to an input string with all found sequences
 * of numbers and periods concatenated together, with any leading period in the first sequence removed.
 * @example @param inputValues - ['#Result.1.2.840.114350.1.13.297.3.7.2.798268.1670845.Comp2']
 * @example @returns - ['1.2.840.114350.1.13.297.3.7.2.798268.1670845']
 */
export declare function extractNumbersAndPeriods(
  inputValues: string[],
): string[];
/**
 * Truncates up to the character limit. If it stops in the middle of the word, it removes the whole word.
 * @param input_str - The string to truncate
 * @param character_limit - The number of characters to truncate defaults to 30
 * @returns - The string that was
 */
export declare const truncateLabNameWholeWord: (
  input_str: string,
  character_limit?: number,
) => string;
/**
 * Converts a string to sentence case, making the first character uppercase and the rest lowercase.
 * @param str - The string to convert to sentence case.
 * @returns The converted sentence-case string. If the input is empty or not a string, the original input is returned.
 */
export declare function toSentenceCase(str: string): string;
/**
 * Adds a caption to a table element.
 * @param element - The React element representing the table.
 * @param caption - The caption text to be added.
 * @param tooltip - Tooltip for caption
 * @returns A React element with the caption added as the first child of the table.
 */
export declare const addCaptionToTable: (
  element: React.ReactNode,
  caption: string,
  tooltip?: string,
) =>
  | string
  | number
  | boolean
  | React.ReactElement<any, string | React.JSXElementConstructor<any>>
  | Iterable<React.ReactNode>
  | null
  | undefined;
/**
 * Removes HTML tags from a given string.
 * @param element - The input string containing HTML elements.
 * @returns - A string with all HTML tags removed.
 */
export declare const removeHtmlElements: (element: string) => string;
