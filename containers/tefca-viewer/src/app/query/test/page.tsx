"use client";
import React, { Suspense, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../../query-service";

// Add a comment to suppress the TypeScript error
// @ts-ignore
import ResultsView from "../components/ResultsView";
import PatientSearchResults from "../components/PatientSearchResults";
import SearchForm from "../components/searchForm/SearchForm";
import { Mode, USE_CASES, ValueSetItem } from "../../constants";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [useCase, setUseCase] = useState<USE_CASES>("" as USE_CASES);
  const [mode, setMode] = useState<Mode>("search");
  const [loading, setLoading] = useState<boolean>(false);
  const [useCaseQueryResponse, setUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>();
  const [originalRequest, setOriginalRequest] = useState<UseCaseQueryRequest>();

  // Just some dummy variables to placate typescript until we delete this page
  const [queryValueSets, _] = useState<ValueSetItem[]>([]);

  return (
    <div>
      {mode === "search" && (
        <Suspense fallback="...Loading">
          <SearchForm
            useCase={useCase}
            queryValueSets={queryValueSets}
            setUseCase={setUseCase}
            setMode={setMode}
            setLoading={setLoading}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
            setOriginalRequest={setOriginalRequest}
            setQueryType={() => {}}
          />
        </Suspense>
      )}

      {/* Switch the mode to view to show the results of the query */}
      {mode === "results" && (
        <>
          {useCaseQueryResponse && (
            <ResultsView
              useCaseQueryResponse={useCaseQueryResponse}
              goBack={() => setMode("search")}
              queryName={useCase}
            />
          )}
        </>
      )}

      {/* Show the multiple patients view if there are multiple patients */}
      {mode === "patient-results" && originalRequest && (
        <>
          <PatientSearchResults
            patients={useCaseQueryResponse?.Patient ?? []}
            originalRequest={originalRequest}
            queryValueSets={queryValueSets}
            setLoading={setLoading}
            goBack={() => setMode("search")}
            setMode={setMode}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
          />
        </>
      )}
      {loading && (
        <div className="overlay">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
};
export default Query;
