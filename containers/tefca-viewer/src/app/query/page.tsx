"use client";
import React, { useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../query-service";
import QueryView from "./components/QueryView";
import MultiplePatientSearchResults from "./components/MultiplePatientSearchResults";
import SearchForm from "./components/SearchForm";
export type Mode = "search" | "results" | "multiple-patients" | "no-patients";

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

  return (
    <div>
      {mode === "search" && (
        <SearchForm
          setMode={setMode}
          setLoading={setLoading}
          setUseCaseQueryResponse={setUseCaseQueryResponse}
          setOriginalRequest={setOriginalRequest}
        />
      )}

      {/* Switch the mode to view to show the results of the query */}
      {mode === "results" && (
        <>
          <button className="usa-button" onClick={() => setMode("search")}>
            Search for a new patient
          </button>
          <LoadingView loading={loading} />
          {/* TODO: add error view if loading is done and there's no useCaseQueryResponse */}
          {useCaseQueryResponse && (
            <QueryView useCaseQueryResponse={useCaseQueryResponse} />
          )}
        </>
      )}

      {/* Show the multiple patients view if there are multiple patients */}
      {mode === "multiple-patients" && originalRequest && (
        <>
          <MultiplePatientSearchResults
            patients={useCaseQueryResponse?.patients ?? []}
            originalRequest={originalRequest}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
            setMode={setMode}
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
