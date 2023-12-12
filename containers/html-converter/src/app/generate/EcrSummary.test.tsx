import {render} from "@testing-library/react";
import EcrSummary from "@/app/generate/EcrSummary";
import fs from "fs";
import {Bundle} from "fhir/r4";
import YAML from 'yaml'
import {expect} from "@jest/globals";

describe("EcrSummary", () => {
    it("should display properly", () => {
        const fhirPathFile = fs.readFileSync('./src/app/generate/fhirPath.yml', 'utf8').toString();
        const fhirPathMappings = YAML.parse(fhirPathFile);
        const fhirBundle: Bundle = JSON.parse(fs.readFileSync('./src/app/generate/exampleBundle.json', 'utf8').toString());

        const {container} = render(<EcrSummary fhirPathMappings={fhirPathMappings} fhirBundle={fhirBundle} />);
        expect(container).toMatchSnapshot();
    });
})