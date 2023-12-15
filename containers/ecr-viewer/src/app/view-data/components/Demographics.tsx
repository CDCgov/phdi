import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";

interface EcrViewerProps {
    fhirPathMappings: PathMappings
    fhirBundle: Bundle
}

interface PathMappings {
    [key: string]: string;
}

const Demographics = (
    { fhirPathMappings, fhirBundle }: EcrViewerProps
) => {
    return (
        <div>
            <div
                className="padding-bottom-3"
                aria-labelledby="summary-box-key-information"
            >
                <div className="usa-summary-box__body">
                    <h3
                        className="usa-summary-box__heading padding-top-105 padding-bottom-1"
                        id="summary-box-key-information"
                    >
                        Demographics
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient Name</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ")} {evaluate(fhirBundle, fhirPathMappings.patientFamilyName)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient ID</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientId)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">DOB</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientDOB)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Sex</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientGender)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Race</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientRace)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Ethnicity</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientEthnicity)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Preferred Language</div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientLanguage)}
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Patient Address</div>
                            <div className="grid-col-auto text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n")} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientCity)}, {evaluate(fhirBundle, fhirPathMappings.patientState)} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientZipCode)}, USA
                            </div>
                        </div>
                        <div className={"section__line_gray margin-y-105"} />
                        <div className="grid-row">
                            <div className="grid-col-2 text-bold">Contact</div>
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
                        <div className={"section__line_gray margin-y-105"} />
                    </div>
                </div>
            </div>
        </div>);
};

export default Demographics;