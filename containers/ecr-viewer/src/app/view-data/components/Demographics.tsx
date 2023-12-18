import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";
import { PathMappings } from "@/app/utils";

interface DemographicsProps {
    fhirPathMappings: PathMappings
    fhirBundle: Bundle | undefined
}



const patientName = (fhirBundle: Bundle | undefined, fhirPathMappings: PathMappings) => {
    const givenNames = evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ");
    const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

    return `${givenNames} ${familyName}`;
}


const Demographics = (
    { fhirPathMappings, fhirBundle }: DemographicsProps
) => {
    return (
        <div>
            <div
                className="padding-bottom-3"
                aria-labelledby="summary-box-key-information"
            >
                <div className="usa-summary-box__body">
                    <h3
                        className="usa-summary-box__heading padding-y-105"
                        id="summary-box-key-information"
                    >
                        Demographics
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Name</h4></div>
                            <div className="grid-col-auto">
                                {patientName(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient ID</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientId)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>DOB</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientDOB)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Sex</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientGender)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Race</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientRace)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Ethnicity</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientEthnicity)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Preferred Language</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.patientLanguage)}
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Address</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n")} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientCity)}, {evaluate(fhirBundle, fhirPathMappings.patientState)} {'\n'}
                                {evaluate(fhirBundle, fhirPathMappings.patientZipCode)}, USA
                            </div>
                        </div>
                        <div className={"section__line_gray"} />
                        <div className="grid-row">
                            <div className="data-title"><h4>Contact</h4></div>
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
                        <div className={"section__line_gray"} />
                    </div>
                </div>
            </div>
        </div>);
};

export default Demographics;