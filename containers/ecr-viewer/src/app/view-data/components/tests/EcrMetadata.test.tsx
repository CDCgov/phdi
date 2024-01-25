import { render } from "@testing-library/react";
import fs from "fs";
import { Bundle } from "fhir/r4";
import YAML from "yaml";
import { axe } from "jest-axe";
import EcrMetadata from "../EcrMetadata";

describe("ECR Metadata", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const fhirPathFile = fs
      .readFileSync("./src/app/api/fhir-data/fhirPath.yml", "utf8")
      .toString();
    const fhirPathMappings = YAML.parse(fhirPathFile);
    const fhirBundle: Bundle = JSON.parse(
      fs
        .readFileSync(
          "./seed-scripts/fhir_data/8675309a-7754-r2d2-c3p0-973d9f777777.json",
          "utf8",
        )
        .toString(),
    );

    container = render(
      <EcrMetadata
        fhirPathMappings={fhirPathMappings}
        fhirBundle={fhirBundle}
      />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
