import { UseCaseQueryResponse } from "../patient_search";

type PatientViewProps = {
    useCaseQueryResponse: UseCaseQueryResponse | undefined;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {
    if (useCaseQueryResponse) {
        return (<div>
            <h1>Welcome to the ugly page</h1>
            <h2>Patient ID: {useCaseQueryResponse.patient_id}</h2>
            <p>{JSON.stringify(useCaseQueryResponse.use_case_query_response, null, 4)}</p>

        </div>)
    } else {
        return null;
    }
}