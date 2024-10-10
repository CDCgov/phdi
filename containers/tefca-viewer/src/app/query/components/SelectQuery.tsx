"use client";
import React, { useEffect, useState } from "react";
import { FHIR_SERVERS, USE_CASES, ValueSetItem } from "../../constants";
import CustomizeQuery from "./CustomizeQuery";
import SelectSavedQuery from "./selectQuery/SelectSavedQuery";

import { QueryResponse } from "@/app/query-service";
import { Patient } from "fhir/r4";
import {
  fetchQueryResponse,
  fetchUseCaseValueSets,
} from "./selectQuery/queryHooks";

interface SelectQueryProps {
  onSubmit: () => void; // Callback when the user submits the query
  goBack: () => void;
  selectedQuery: USE_CASES;
  setSelectedQuery: React.Dispatch<React.SetStateAction<USE_CASES>>;
  patientForQuery: Patient | undefined;
  resultsQueryResponse: QueryResponse;
  setResultsQueryResponse: React.Dispatch<React.SetStateAction<QueryResponse>>;
  fhirServer: FHIR_SERVERS;
  setFhirServer: React.Dispatch<React.SetStateAction<FHIR_SERVERS>>;
}

/**
 *
 * @param root0 - SelectQueryProps
 * @param root0.setQueryType - Callback to update the query type
 * @param root0.setHCO - Callback to update selected Health Care Organization (HCO)
 * @param root0.setMode - Callback to switch mode
 * @param root0.onSubmit - Callback for submit action
 * @param root0.goBack - back button
 * @param root0.patientForQuery
 * @param root0.resultsQueryResponse
 * @param root0.setResultsQueryResponse
 * @param root0.selectedQuery
 * @param root0.setSelectedQuery
 * @param root0.fhirServer
 * @param root0.setFhirServer
 * @returns - The selectQuery component.
 */
const SelectQuery: React.FC<SelectQueryProps> = ({
  onSubmit,
  goBack,
  selectedQuery,
  setSelectedQuery,
  patientForQuery,
  resultsQueryResponse,
  setResultsQueryResponse,
  fhirServer,
  setFhirServer,
}) => {
  const [showCustomizeQuery, setShowCustomizedQuery] = useState(false);
  const [queryValueSets, setQueryValueSets] = useState<ValueSetItem[]>(
    [] as ValueSetItem[],
  );
  useEffect(() => {
    // Gate whether we actually update state after fetching so we
    // avoid name-change race conditions
    let isSubscribed = true;

    fetchUseCaseValueSets(selectedQuery, setQueryValueSets, isSubscribed).catch(
      console.error,
    );

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [selectedQuery, setQueryValueSets]);

  useEffect(() => {
    let isSubscribed = true;

    fetchQueryResponse(
      patientForQuery,
      selectedQuery,
      isSubscribed,
      queryValueSets,
      setResultsQueryResponse,
      fhirServer,
    ).catch(console.error);

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [patientForQuery, selectedQuery, queryValueSets, setResultsQueryResponse]);

  return showCustomizeQuery ? (
    <CustomizeQuery
      useCaseQueryResponse={resultsQueryResponse}
      queryType={selectedQuery}
      queryValuesets={queryValueSets}
      setQueryValuesets={setQueryValueSets}
      goBack={() => setShowCustomizedQuery(false)}
    ></CustomizeQuery>
  ) : (
    <SelectSavedQuery
      goBack={goBack}
      selectedQuery={selectedQuery}
      setSelectedQuery={setSelectedQuery}
      setShowCustomizedQuery={setShowCustomizedQuery}
      handleSubmit={onSubmit}
      fhirServer={fhirServer}
      setFhirServer={setFhirServer}
    ></SelectSavedQuery>
  );
};

export default SelectQuery;
export const RETURN_TO_STEP_ONE_LABEL = "Return to Select patient";
