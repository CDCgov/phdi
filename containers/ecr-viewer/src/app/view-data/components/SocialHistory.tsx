import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";

interface EcrViewerProps {
    fhirPathMappings: PathMappings
    fhirBundle: Bundle
}

interface PathMappings {
    [key: string]: string;
}
const SocialHistory = (
    { fhirPathMappings, fhirBundle }: EcrViewerProps
) => {
    const demographicsData = [
        {
            'title': 'Occupation',
            'value': evaluate(fhirBundle, fhirPathMappings.patientCurrentJobTitle)
        },
        {
            'title': 'Tobacco Use',
            'value': evaluate(fhirBundle, fhirPathMappings.patientTobaccoUse)
        },
        {
            'title': 'Travel History',
            'value': evaluate(fhirBundle, fhirPathMappings.patientTravelHistory)
        },
        {
            'title': 'Homeless Status',
            'value': evaluate(fhirBundle, fhirPathMappings.patientHomelessStatus)
        },
        {
            'title': 'Pregnancy Status',
            'value': evaluate(fhirBundle, fhirPathMappings.patientPregnancyStatus)
        },
        {
            'title': 'Alcohol Use',
            'value': evaluate(fhirBundle, fhirPathMappings.patientAlcoholUse)
        },
        {
            'title': 'Sexual Orientation',
            'value': evaluate(fhirBundle, fhirPathMappings.patientSexualOrientation)
        },
        {
            'title': 'Gender Identity',
            'value': evaluate(fhirBundle, fhirPathMappings.patientGenderIdentity)
        },
        {
            'title': 'Occupation',
            'value': evaluate(fhirBundle, fhirPathMappings.patientCurrentJobTitle)
        },

    ]

    const renderDemographicsData = (item: any, index: number) => {
        console.log(item.value.length);
        if (item.value.length > 0) {
            return (
                <div key={index}>
                    <div className="grid-row">
                        <div className="grid-col-2 text-bold">{item.title}</div>
                        <div className="grid-col-auto">
                            {item.value}
                        </div>
                    </div>
                    <div className={"section__line_gray margin-y-105"} />
                </div>
            )
        }
    }

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
                        Social History
                    </h3>
                    <div className="usa-summary-box__text">
                        {demographicsData.map((item, index) => renderDemographicsData(item, index))}
                    </div>
                </div>
            </div>
        </div>);
};

export default SocialHistory;