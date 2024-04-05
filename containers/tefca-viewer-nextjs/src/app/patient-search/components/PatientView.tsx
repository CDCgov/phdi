import { PatientIdQueryResponse } from "../patient_search";

type PatientViewProps = {
    useCaseQueryResponse: PatientIdQueryResponse | undefined;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {
    if (useCaseQueryResponse) {
        return (<div>
            <h2>Patient ID: {useCaseQueryResponse.patient_id}</h2>
            <h2>First Name: {useCaseQueryResponse.first_name}</h2>
        </div>)
    } else {
        return null;
    }
}