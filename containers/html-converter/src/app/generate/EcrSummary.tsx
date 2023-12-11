import {evaluate} from "fhirpath";
import fs from "fs";
import {parse} from "yaml";
import {Bundle} from "fhir/r4";

interface EcrViewerProps {
    fhirBundle: any
}

const EcrSummary = (
    // {fhirBundle}: EcrViewerProps
) => {
    const file = fs.readFileSync('./src/app/generate/fhirPath.yml', 'utf8').toString();
    const fhirBundle: Bundle = JSON.parse(fs.readFileSync('./src/app/generate/exampleBundle.json', 'utf8').toString());
    const fhirPathMappings = parse(file);
    return (
        <div>
            <h1>Quick eCR Summary</h1>
            <div
                className="usa-summary-box padding-3"
                aria-labelledby="summary-box-key-information"
            >
                <div className="usa-summary-box__body">
                    <h3
                        className="usa-summary-box__heading padding-top-105 padding-bottom-1"
                        id="summary-box-key-information"
                    >
                        About the Patient
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient Name</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ")} {evaluate(fhirBundle, fhirPathMappings.patientFamilyName)}
                            </div>
                        </div>
                        <div className={"section__line"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient Address</div>
                            <div className="grid-col-auto text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n")} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientCity)}, {evaluate(fhirBundle, fhirPathMappings.patientState)} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientZipCode)}, USA
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                        <div className="grid-col-2 text-bold">Patient Contact</div>
                            <div className="grid-col-auto text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientPhoneNumbers).map(phoneNumber => {
                                    return `tel: (${phoneNumber.use}) ${phoneNumber.value}`
                                }).join("\n")}
                                {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientEmails).map(email => {
                                    return `email: ${email.value}`
                                }).join("\n")}
                            </div>
                        </div>
                        <div className={"section__line"} />
                    </div>
                </div>
            </div>
        </div>);
};

export default EcrSummary;