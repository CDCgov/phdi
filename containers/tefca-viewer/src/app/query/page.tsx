"use client";
import React, { Suspense, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../query-service";
import ResultsView from "./components/ResultsView";
import MultiplePatientSearchResults from "./components/MultiplePatientSearchResults";
import SearchForm from "./components/SearchForm";
import NoPatientsFound from "./components/NoPatientsFound";
import { Mode } from "../constants";
import CustomizeQuery from "./components/CustomizeQuery";
import LoadingView from "./components/LoadingView";
import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.min.css";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [queryType, setQueryType] = useState<string>("");
  const [mode, setMode] = useState<Mode>("search");
  const [loading, setLoading] = useState<boolean>(false);
  const [useCaseQueryResponse, setUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>({});
  const [originalRequest, setOriginalRequest] = useState<UseCaseQueryRequest>();

  return (
    <div>
      {mode === "search" && (
        <Suspense fallback="...Loading">
          <SearchForm
            setMode={setMode}
            setLoading={setLoading}
            setUseCaseQueryResponse={setUseCaseQueryResponse}
            setOriginalRequest={setOriginalRequest}
            setQueryType={setQueryType}
            userJourney="demo"
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

      {/* Use LoadingView component for loading state */}
      <LoadingView loading={loading} />

      {/* Show the customize query view to select and change what is returned in results */}
      {mode === "customize-queries" && (
        <>
          <CustomizeQuery
            useCaseQueryResponse={useCaseQueryResponse}
            queryType={queryType}
            goBack={() => {
              setMode("search");
            }}
          />
        </>
      )}
      <ToastContainer icon={false} />
    </div>
  );
};

export default Query;
