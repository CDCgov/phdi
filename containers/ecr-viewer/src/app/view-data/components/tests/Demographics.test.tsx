import { render } from "@testing-library/react";
import fs from "fs";
import { Bundle } from "fhir/r4";
import YAML from "yaml";
import { axe } from "jest-axe";
import Demographics from "@/app/view-data/components/Demographics";

describe("Demographics", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const fhirPathFile = fs
      .readFileSync("./src/app/api/fhir-data/fhirPath.yml", "utf8")
      .toString();
    const fhirPathMappings = YAML.parse(fhirPathFile);
    const fhirBundle: Bundle = JSON.parse(
      fs
        .readFileSync(
          "./seed-scripts/fhir_data/1dd10047-2207-4eac-a993-0f706c88be5d.json",
          "utf8",
        )
        .toString(),
    );

    container = render(
      <Demographics
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
