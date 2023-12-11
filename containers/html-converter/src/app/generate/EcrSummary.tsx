import {evaluate} from "fhirpath";
import fs from "fs";
import {parse} from "yaml";
import {Bundle} from "fhir/r4";

interface EcrViewerProps {
    fhirPathMappings: any
    fhirBundle: Bundle
}

const EcrSummary = (
    {fhirPathMappings, fhirBundle}: EcrViewerProps
) => {
    let givenNames = evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ");
    let familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);
    let streetAddresses = evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n");
    let city = evaluate(fhirBundle, fhirPathMappings.patientCity);
    let state = evaluate(fhirBundle, fhirPathMappings.patientState);
    let zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode);
    let phoneNumbers = evaluate(fhirBundle, fhirPathMappings.patientPhoneNumbers).map(phoneNumber => `tel: (${phoneNumber.use}) ${phoneNumber.value}`).join("\n");
    let emails = evaluate(fhirBundle, fhirPathMappings.patientEmails).map(email => `email: ${email.value}`).join("\n");
    return (
        <div>
            <h2>Quick eCR Summary</h2>
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
                                {givenNames} {familyName}
                            </div>
                        </div>
                        <div className={"section__line"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient Address</div>
                            <div className="grid-col-auto text-pre-line">
                                {streetAddresses} {'\n'}
                                {city}, {state} {'\n'}
                                {zipCode}, USA
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                        <div className="grid-col-2 text-bold">Patient Contact</div>
                            <div className="grid-col-auto text-pre-line">
                                {phoneNumbers}
                                {'\n'}
                                {emails}
                            </div>
                        </div>
                        <div className={"section__line"} />
                    </div>
                </div>
            </div>
        </div>);
};

export default EcrSummary;