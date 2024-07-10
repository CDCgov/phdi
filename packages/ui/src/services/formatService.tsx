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
