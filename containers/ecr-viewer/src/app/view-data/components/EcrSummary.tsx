import {evaluate} from "fhirpath";
import {Bundle} from "fhir/r4";
import {
    PathMappings,
    formatPatientName,
    extractPatientAddress,
    formatPatientContactInfo,
    extractFacilityAddress, formatEncounterDate
} from "../../utils";

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
                            <div className="grid-col-auto">
                                {formatPatientName(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>DOB</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {evaluate(fhirBundle, fhirPathMappings.patientDOB)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Address</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {extractPatientAddress(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Patient Contact</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {formatPatientContactInfo(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                    </div>
                </div>
                <div className="usa-summary-box__body">
                    <h3 id="summary-box-key-information">
                        About the Encounter
                    </h3>
                    <div className="usa-summary-box__text">
                        <div className="grid-row">
                            <div className="data-title"><h4>Facility Name</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.facilityName)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Facility Address</h4></div>
                            <div className="grid-col-auto text-pre-line">
                                {extractFacilityAddress(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Encounter Type</h4></div>
                            <div className="grid-col-auto">
                                {evaluate(fhirBundle, fhirPathMappings.encounterType)}
                            </div>
                        </div>
                        <div className={"section__line"}/>
                        <div className="grid-row">
                            <div className="data-title"><h4>Encounter Date</h4></div>
                            <div className="grid-col-auto">
                                {formatEncounterDate(fhirBundle, fhirPathMappings)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>);
};

export default EcrSummary;