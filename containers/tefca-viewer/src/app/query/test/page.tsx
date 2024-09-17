"use client";
import React, { Suspense, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../../query-service";

// Add a comment to suppress the TypeScript error
// @ts-ignore
import ResultsView from "../components/ResultsView";
import MultiplePatientSearchResults from "../components/MultiplePatientSearchResults";
import SearchForm from "../components/SearchForm";
import NoPatientsFound from "../components/NoPatientsFound";
import { Mode, USE_CASES } from "../../constants";

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

  return (
    <div>
      {mode === "search" && (
        <Suspense fallback="...Loading">
          <SearchForm
            useCase={useCase}
            setUseCase={setUseCase}
            setMode={setMode}
            setLoading={setLoading}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
            setOriginalRequest={setOriginalRequest}
            userJourney="test"
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
            />
          )}
        </>
      )}

      {/* Show the multiple patients view if there are multiple patients */}
      {mode === "multiple-patients" && originalRequest && (
        <>
          <MultiplePatientSearchResults
            patients={useCaseQueryResponse?.Patient ?? []}
            originalRequest={originalRequest}
            setLoading={setLoading}
            goBack={() => setMode("search")}
          />
        </>
      )}
      {/* Show the no patients found view if there are no patients */}
      {mode === "no-patients" && <NoPatientsFound setMode={setMode} />}
      {loading && (
        <div className="overlay">
          <div className="spinner"></div>
        </div>
      )}
    </div>
  );
};
export default Query;
