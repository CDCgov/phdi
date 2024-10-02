import React, { Fragment, useEffect, useState } from "react";
import { Patient } from "fhir/r4";

import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import { ValueSetItem } from "@/app/constants";
import Backlink from "./backLink/Backlink";
import PatientSearchResultsTable from "./patientSearchResults/PatientSearchResultsTable";
import ResultsView from "./ResultsView";
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
 * @returns - The PatientSearchResults component.
 */
const PatientSearchResults: React.FC<PatientSearchResultsProps> = ({
  patients,
  originalRequest,
  queryValueSets,
  setLoading,
  goBack,
}) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  // Determines whether to show the results of a single patient (ResultsView) or
  // go back to the multiple patients view (below)
  const [singleUseCaseQueryResponse, setSingleUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>();
  const [patientForQuery, setPatientForQueryResponse] = useState<Patient>();

  useEffect(() => {
    let isSubscribed = true;

    const fetchQuery = async () => {
      if (patientForQuery) {
        setLoading(true);
        const queryResponse = await UseCaseQuery(
          originalRequest,
          queryValueSets,
          {
            Patient: [patientForQuery],
          },
        );
        setSingleUseCaseQueryResponse(queryResponse);

        setLoading(false);
      }
    };

    fetchQuery().catch(console.error);

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [patientForQuery]);

  if (singleUseCaseQueryResponse) {
    // If a single patient is selected, show the button for returning to the search results
    // & take user back to the search results by setting the singleUseCaseQueryResponse to undefined
    return (
      <ResultsView
        useCaseQueryResponse={singleUseCaseQueryResponse}
        goBack={goBack}
        goBackToMultiplePatients={() =>
          setSingleUseCaseQueryResponse(undefined)
        }
        queryName={originalRequest.use_case}
      />
    );
  }
  return (
    <>
      <div className="multiple-patient-search-results">
        <Backlink onClick={goBack} label={"Return to Enter patient info"} />
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
      </div>
    </>
  );
};

export default PatientSearchResults;
