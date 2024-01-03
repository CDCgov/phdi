import {evaluate} from "fhirpath";
import {Bundle} from "fhir/r4";
import {PathMappings, formatPatientName, formatPatientAddress, formatPatientContactInfo} from "../../utils";

interface EcrViewerProps {
    fhirPathMappings: PathMappings
    fhirBundle: Bundle
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
                            <div className="grid-col-fill">
                                {formatPatientName(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>DOB</h4></div>
                            <div className="grid-col-fill text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientDOB)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Address</h4></div>
                            <div className="grid-col-fill text-pre-line">
                                {formatPatientAddress(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Contact</h4></div>
                            <div className="grid-col-fill text-pre-line">
                                {formatPatientContactInfo(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                    </div>
                </div>
                <div className="usa-summary-box__body">
                    <h3 id="summary-box-key-information">
                        About the Condition
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="data-title"><h4>Reportable Condition</h4></div>
                            <div className="grid-col-fill">
                                {evaluate(fhirBundle, fhirPathMappings.rrDisplayName)[0].split('-')[1]}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>RCKMS Trigger Summary</h4></div>
                            <div className="grid-col-fill text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.rckmsTriggerSummary)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                                <h4>Lab results relevant to reportable condition</h4>
                            <div className="usa-card__container margin-left-0 margin-right-0 margin-top-1">
                                <div className="usa-card__header padding-top-2 padding-bottom-2 padding-left-3">
                                    <p>
                                        Hepatitis C IgG w/Rfx PCR (temp)<span
                                        className="usa-tag margin-left-1 bg-error-dark text-white">Abnormal</span>
                                    </p>
                                </div>
                                <div className={"card__line "}/>
                                <div className="usa-card__body padding-0">
                                    <table className="usa-table usa-table--borderless ecrTable">
                                        <thead>
                                        <tr>
                                            <th scope="col">Component</th>
                                            <th scope="col">Value</th>
                                            <th scope="col">Ref Range</th>
                                            <th scope="col">Specimen</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        <tr>
                                            <td>Hepatitis C Antibody (temp)</td>
                                            <td>Positive (A) (temp)</td>
                                            <td>Not Detected (temp)</td>
                                            <td>Blood (temp)</td>
                                        </tr>
                                        </tbody>
                                    </table>
                                    <div className={"card__line"}/>
                                    <div
                                        className={"padding-left-3 padding-right-3 padding-top-205 padding-bottom-205"}>
                                        <div className="grid-row">
                                            <div className="data-title"><h4>Analysis time</h4></div>
                                            <div className="grid-col-fill text-pre-line">
                                                N/A (temp)
                                            </div>
                                        </div>
                                        <div className={"section__line_gray"}/>
                                        <div className="grid-row">
                                            <div className="data-title"><h4>Collection time</h4></div>
                                            <div className="grid-col-fill text-pre-line">
                                                05/12/2022 6:00 AM CDT (temp)
                                            </div>
                                        </div>
                                        <div className={"section__line_gray"}/>
                                        <div className="grid-row">
                                            <div className="data-title"><h4>Received time</h4></div>
                                            <div className="grid-col-fill text-pre-line">
                                                05/12/2022 11:30 AM CDT (temp)
                                            </div>
                                        </div>
                                        <div className={"section__line_gray"}/>
                                        <div className="grid-row">
                                            <div className="data-title"><h4>Notes</h4></div>
                                            <div className="grid-col-fill text-pre-line">
                                                A detected result is positive and indicates the presence of the virus in
                                                the sample. A not detected result indicates that the test did not detect
                                                the virus in the sample. This test was performed using a multiplexed
                                                nucleic acid amplification test that is labeled Emergence Use Only by
                                                the U.S. FDA. Results of this test should not be used as the sole basis
                                                for diagnosis, treatment, or other management decisions. (temp)
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <h4>Clinical sections relevant to reportable condition</h4>
                            <div className={"padding-top-05"}>No matching clinical data found in this eCR (temp) </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>);
};

export default EcrSummary;