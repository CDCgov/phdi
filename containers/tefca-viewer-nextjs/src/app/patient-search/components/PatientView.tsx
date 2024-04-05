import { UseCaseQueryResponse } from "../patient_search";

type PatientViewProps = {
    useCaseQueryResponse: UseCaseQueryResponse | undefined;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {
    if (useCaseQueryResponse) {
        return (<div>
            <h2>Patient ID: {useCaseQueryResponse.patient_id}</h2>
            <pre>{JSON.stringify(useCaseQueryResponse.use_case_query_response, null, 2)}</pre>
        </div>)
    } else {
        return null;
    }
}