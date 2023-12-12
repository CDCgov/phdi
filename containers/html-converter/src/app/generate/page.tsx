import EcrSummary from "@/app/generate/EcrSummary";
import fs from "fs";
import { Bundle } from "fhir/r4";
import { parse } from "yaml";

const EcrViewer = () => {
  const file = fs
    .readFileSync("./src/app/generate/fhirPath.yml", "utf8")
    .toString();
  const fhirBundle: Bundle = JSON.parse(
    fs.readFileSync("./src/app/generate/exampleBundle.json", "utf8").toString(),
  );
  const fhirPathMappings = parse(file);

  return (
    <div>
      <EcrSummary fhirPathMappings={fhirPathMappings} fhirBundle={fhirBundle} />
    </div>
  );
};

export default EcrViewer;
