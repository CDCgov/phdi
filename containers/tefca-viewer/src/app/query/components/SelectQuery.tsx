"use client";
import React, { useEffect, useState } from "react";
import { Mode, USE_CASES, ValueSetItem } from "../../constants";
import CustomizeQuery from "./CustomizeQuery";
import SelectSavedQuery from "./selectQuery/SelectSavedQuery";

import { QueryResponse } from "@/app/query-service";
import { Patient } from "fhir/r4";
import {
  fetchQueryResponse,
  fetchUseCaseValueSets,
} from "./selectQuery/queryHooks";

interface SelectQueryProps {
  setMode: (mode: Mode) => void;
  onSubmit: () => void; // Callback when the user submits the query
  goBack: () => void;
  patientForQuery: Patient | undefined;
  resultsQueryResponse: QueryResponse;
  setResultsQueryResponse: React.Dispatch<React.SetStateAction<QueryResponse>>;
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
 * @returns - The selectQuery component.
 */
const SelectQuery: React.FC<SelectQueryProps> = ({
  setMode,
  onSubmit,
  goBack,
  patientForQuery,
  resultsQueryResponse,
  setResultsQueryResponse,
}) => {
  const [selectedQuery, setSelectedQuery] = useState<USE_CASES>("cancer");
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
      goBack={() => setMode("patient-results")}
      setSelectedQuery={setSelectedQuery}
      selectedQuery={selectedQuery}
      setShowCustomizedQuery={setShowCustomizedQuery}
      handleSubmit={() => setMode("results")}
    ></SelectSavedQuery>
  );
};

export default SelectQuery;
export const RETURN_TO_STEP_ONE_LABEL = "Return to Select patient";
