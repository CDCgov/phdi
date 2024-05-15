import * as fs from "fs";
import * as path from "path";
import yaml from "js-yaml";
import { PathMappings } from "@/app/utils";

/**
 * Loads the YAML configuration for path mappings from a predefined file location.
 * @returns An object representing the path mappings defined in the YAML configuration file.
 */
export function loadYamlConfig(): PathMappings {
  const filePath = path.join(
    process.cwd(),
    "src/app/api/services/fhirPath.yml",
  );
  const fileContents = fs.readFileSync(filePath, "utf8");
  return <PathMappings>yaml.load(fileContents);
}

/**
 * Converts stream data to json data
 * @param stream - The input stream that provides JSON data in chunks. The stream
 *   should implement the async iterable protocol to allow for-await-of
 *   iteration over its data chunks.
 * @returns A promise that resolves to the JSON-parsed object from the accumulated
 *  stream data. The specific structure of this object depends on the JSON
 *  content of the stream.
 */
export async function streamToJson(stream: any) {
  let rawData = "";
  for await (const chunk of stream) {
    rawData += chunk;
  }
  return JSON.parse(rawData);
}
