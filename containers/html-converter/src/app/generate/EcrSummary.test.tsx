import {render} from "@testing-library/react";
import EcrSummary from "@/app/generate/EcrSummary";
import fs from "fs";
import {Bundle} from "fhir/r4";
import YAML from 'yaml'
import {axe} from "jest-axe";

describe("EcrSummary", () => {
    let container: HTMLElement
    beforeAll(() =>{
        const fhirPathFile = fs.readFileSync('./src/app/generate/fhirPath.yml', 'utf8').toString();
        const fhirPathMappings = YAML.parse(fhirPathFile);
        const fhirBundle: Bundle = JSON.parse(fs.readFileSync('./src/app/generate/exampleBundle.json', 'utf8').toString());

         container = render(<EcrSummary fhirPathMappings={fhirPathMappings} fhirBundle={fhirBundle} />).container;
    })
    it("should match snapshot", () => {
        expect(container).toMatchSnapshot();
    });
    it("should pass accessibility test", async () => {
        expect(await axe(container)).toHaveNoViolations()
    })
})