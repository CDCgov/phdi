import {evaluate} from "fhirpath";
import {Bundle} from "fhir/r4";

interface EcrViewerProps {
    fhirPathMappings: PathMappings
    fhirBundle: Bundle
}

interface PathMappings {
    [key: string]: string;
}

const patientAddress = (fhirBundle: Bundle, fhirPathMappings: PathMappings) => {
    const streetAddresses = evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n");
    const city = evaluate(fhirBundle, fhirPathMappings.patientCity);
    const state = evaluate(fhirBundle, fhirPathMappings.patientState);
    const zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode);
    const country = evaluate(fhirBundle, fhirPathMappings.patientCountry);
    return(
    `${streetAddresses}
    ${city}, ${state}
    ${zipCode}${country && `, ${country}`}`);
}

const patientName = (fhirBundle: Bundle, fhirPathMappings: PathMappings) => {
    const givenNames = evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ");
    const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

    return `${givenNames} ${familyName}`;
}

const patientContactInfo = (fhirBundle: Bundle, fhirPathMappings: PathMappings) => {
    const phoneNumbers = evaluate(fhirBundle, fhirPathMappings.patientPhoneNumbers).map(phoneNumber => `tel: (${phoneNumber.use}) ${phoneNumber.value}`).join("\n");
    const emails = evaluate(fhirBundle, fhirPathMappings.patientEmails).map(email => `email: ${email.value}`).join("\n");

    return `${phoneNumbers}
    ${emails}`
}


const EcrSummary = (
    {fhirPathMappings, fhirBundle}: EcrViewerProps
) => {
    return (
        <div className={"info-container"}>
            <div
                className="usa-summary-box padding-3"
                aria-labelledby="summary-box-key-information"
            >
                <div className="usa-summary-box__body">
                    <h3 id="summary-box-key-information">
                        About the Patient
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Name</h4></div>
                            <div className="grid-col-auto">
                                {patientName(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Address</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {patientAddress(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Contact</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {patientContactInfo(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"} />
                    </div>
                </div>
            </div>
        </div>);
};

export default EcrSummary;