/**
 * @jest-environment node
 */

import * as fs from "fs";

/**
 * Helper function to read a JSON file from a given file path.
 * @param filePath The relative string path to the file.
 * @returns A JSON object of the string representation of the file.
 */
export function readJsonFile(filePath: string): any {
  try {
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading JSON file from ${filePath}:`, error);
    return null;
  }
}
