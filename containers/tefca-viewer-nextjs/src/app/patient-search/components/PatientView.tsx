import { PatientIdQueryResponse, UseCaseQueryResponse } from "../patient_search";

type PatientViewProps = {
    useCaseQueryResponse: UseCaseQueryResponse | undefined;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {
    if (useCaseQueryResponse) {
        return (<div>
            <h2>Patient ID: {useCaseQueryResponse.patient_id as string}</h2>
            <h2>FHIR host: {useCaseQueryResponse.fhir_host as string}</h2>
        </div>)
    } else {
        return null;
    }
}