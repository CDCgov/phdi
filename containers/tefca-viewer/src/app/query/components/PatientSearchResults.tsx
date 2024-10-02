import React, { useEffect, useState } from "react";
import { Patient } from "fhir/r4";

import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import { Mode, ValueSetItem } from "@/app/constants";
import Backlink from "./backLink/Backlink";
import PatientSearchResultsTable from "./patientSearchResults/PatientSearchResultsTable";
import NoPatientsFound from "./patientSearchResults/NoPatientsFound";

/**
 * The props for the PatientSearchResults component.
 */
export interface PatientSearchResultsProps {
  patients: Patient[];
  originalRequest: UseCaseQueryRequest;
  queryValueSets: ValueSetItem[];
  setLoading: (loading: boolean) => void;
  goBack: () => void;
  setMode: (mode: Mode) => void;
  setUseCaseQueryResponse: (UseCaseQueryResponse: UseCaseQueryResponse) => void;
}

/**
 * Displays multiple patient search results in a table.
 * @param root0 - PatientSearchResults props.
 * @param root0.patients - The array of Patient resources.
 * @param root0.originalRequest - The original request object.
 * @param root0.queryValueSets - The stateful collection of value sets to include
 * in the query.
 * @param root0.setLoading - The function to set the loading state.
 * @param root0.goBack - The function to go back to the previous page.
 * @param root0.setUseCaseQueryResponse - State update function to pass the
 * data needed for the results view back up to the parent component
 * @param root0.setMode - Redirect function to handle results view routing
 * @returns - The PatientSearchResults component.
 */
const PatientSearchResults: React.FC<PatientSearchResultsProps> = ({
  patients,
  originalRequest,
  queryValueSets,
  setLoading,
  goBack,
  setUseCaseQueryResponse,
  setMode,
}) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  const [patientForQuery, setPatientForQueryResponse] = useState<Patient>();

  useEffect(() => {
    let isSubscribed = true;

    const fetchQuery = async () => {
      if (patientForQuery && isSubscribed) {
        setLoading(true);
        const queryResponse = await UseCaseQuery(
          originalRequest,
          queryValueSets,
          {
            Patient: [patientForQuery],
          },
        );
        setUseCaseQueryResponse(queryResponse);
        setMode("results");
        setLoading(false);
      }
    };

    fetchQuery().catch(console.error);

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [patientForQuery]);

  return (
    <>
      <Backlink onClick={goBack} label={RETURN_TO_STEP_ONE_LABEL} />
      {patients.length === 0 && (
        <>
          <NoPatientsFound />
          <a href="#" className="usa-link" onClick={goBack}>
            Revise your patient search
          </a>
        </>
      )}
      {patients.length > 0 && (
        <>
          <PatientSearchResultsTable
            patients={patients}
            setPatientForQueryResponse={setPatientForQueryResponse}
          />

          <h3 className="margin-top-5 margin-bottom-1">
            Not seeing what you're looking for?
          </h3>

          <a href="#" className="usa-link" onClick={goBack}>
            Return to patient search
          </a>
        </>
      )}
    </>
  );
};

export default PatientSearchResults;
export const RETURN_TO_STEP_ONE_LABEL = "Return to Enter patient info";
