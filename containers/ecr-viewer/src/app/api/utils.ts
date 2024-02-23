import * as fs from "fs";
import * as path from "path";
import yaml from "js-yaml";
import { PathMappings } from "@/app/utils";

export function loadYamlConfig(): PathMappings {
  const filePath = path.join(process.cwd(), "src/app/api/fhirPath.yml");
  const fileContents = fs.readFileSync(filePath, "utf8");
  return <PathMappings>yaml.load(fileContents);
}

export async function streamToJson(stream: any) {
  let rawData = "";
  for await (const chunk of stream) {
    rawData += chunk;
  }
  return JSON.parse(rawData);
}
