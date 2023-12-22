import * as fs from 'fs';
import * as path from 'path';
import yaml from 'js-yaml';

export function loadYamlConfig() {
  const filePath = path.join(process.cwd(), 'src/app/api/fhir-data/fhirPath.yml');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  const data = yaml.load(fileContents);
  return data;
}
