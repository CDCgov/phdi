import {parse} from "yaml";

const fetchYamlData = async () => {
  const response = await fetch('/fhirPath.yml');
  const text = await response.text();
  return parse(text);
};

export const fhirPathMappings = fetchYamlData();
