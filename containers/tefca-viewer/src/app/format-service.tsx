/**
 * Formats a string.
 * @param {string} input - The string to format.
 * @returns {string} The formatted string.
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
