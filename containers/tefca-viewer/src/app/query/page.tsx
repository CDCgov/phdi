"use client";
import React, { Suspense, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../query-service";
import ResultsView from "./components/ResultsView";
import MultiplePatientSearchResults from "./components/MultiplePatientSearchResults";
import SearchForm from "./components/SearchForm";
import NoPatientsFound from "./components/NoPatientsFound";
import {
  Mode,
  demoQueryOptions,
  dummyConditions,
  dummyLabs,
  dummyMedications,
  USE_CASES,
} from "../constants";
import CustomizeQuery from "./components/CustomizeQuery";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [mode, setMode] = useState<Mode>("search");
  const [loading, setLoading] = useState<boolean>(false);
  const [useCaseQueryResponse, setUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>();
  const [originalRequest, setOriginalRequest] = useState<UseCaseQueryRequest>();
  const [useCase, setUseCase] = useState("cancer");
  const [queryType, setQueryType] = useState<string>(
    demoQueryOptions.find((option) => option.value === useCase)?.label || "",
  );

  return (
    <div>
      {mode === "search" && (
        <Suspense fallback="...Loading">
          <SearchForm
            setMode={setMode}
            setLoading={setLoading}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
            setOriginalRequest={setOriginalRequest}
            setUseCase={setUseCase}
            setQueryType={setQueryType}
            userJourney="demo"
            useCase={useCase as USE_CASES}
          />
        </Suspense>
      )}

      {/* Switch the mode to view to show the results of the query */}
      {mode === "results" && (
        <>
          {useCaseQueryResponse && (
            <ResultsView
              useCaseQueryResponse={useCaseQueryResponse}
              goBack={() => {
                setMode("search");
              }}
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

      {mode === "customize-queries" && (
        <>
          <CustomizeQuery
            queryType={queryType}
            ValueSet={{
              labs: dummyLabs,
              medications: dummyMedications,
              conditions: dummyConditions,
            }}
            goBack={() => setMode("search")}
          />
        </>
      )}
    </div>
  );
};
export default Query;
function LoadingView({ loading }: { loading: boolean }) {
  if (loading) {
    return (
      <div>
        <h2>Loading...</h2>
      </div>
    );
  } else {
    return null;
  }
}
