"use client";
import React, { Suspense, useEffect, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../query-service";
import ResultsView from "./components/ResultsView";
import PatientSearchResults from "./components/PatientSearchResults";
import SearchForm from "./components/searchForm/SearchForm";
import SelectQuery from "./components/selectQuery/selectQuery";
import {
  Mode,
  QueryTypeToQueryName,
  USE_CASES,
  ValueSetItem,
} from "../constants";
import CustomizeQuery from "./components/CustomizeQuery";
import LoadingView from "./components/LoadingView";
import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.min.css";
import {
  getSavedQueryByName,
  mapQueryRowsToValueSetItems,
} from "../database-service";
import SiteAlert from "./designSystem/SiteAlert";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [useCase, setUseCase] = useState<USE_CASES>("" as USE_CASES);
  const [queryType, setQueryType] = useState<string>("");
  const [queryValuesets, setQueryValuesets] = useState<ValueSetItem[]>(
    [] as ValueSetItem[],
  );
  const [mode, setMode] = useState<Mode>("search");
  const [loading, setLoading] = useState<boolean>(false);
  const [useCaseQueryResponse, setUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>({});
  const [originalRequest, setOriginalRequest] = useState<UseCaseQueryRequest>();

  useEffect(() => {
    // Gate whether we actually update state after fetching so we
    // avoid name-change race conditions
    let isSubscribed = true;

    const queryName = QueryTypeToQueryName[queryType];
    const fetchQuery = async () => {
      const queryResults = await getSavedQueryByName(queryName);
      const vsItems = await mapQueryRowsToValueSetItems(queryResults);

      // Only update if the fetch hasn't altered state yet
      if (isSubscribed) {
        setQueryValuesets(vsItems);
      }
    };

    fetchQuery().catch(console.error);

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [queryType]);

  return (
    <>
      <SiteAlert page={mode} />
      <div className="main-container">
        {mode === "search" && (
          <>
            <Suspense fallback="...Loading">
              <SearchForm
                useCase={useCase}
                queryValueSets={queryValuesets}
                setUseCase={setUseCase}
                setMode={setMode}
                setLoading={setLoading}
                setUseCaseQueryResponse={setUseCaseQueryResponse}
                setOriginalRequest={setOriginalRequest}
                setQueryType={setQueryType}
              />
            </Suspense>
          </>
        )}

        {/* Render SelectQuery component when the mode is "select-query" */}
        {mode === "select-query" && (
          <SelectQuery
            setQueryType={setQueryType}
            setHCO={() => {}}
            setMode={setMode}
            goBack={() => setMode("patient-results")}
            onSubmit={() => setMode("results")}
          />
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
                queryName={queryType}
              />
            )}
          </>
        )}

        {/* Show the patients results view if there are multiple patients */}
        {mode === "patient-results" && originalRequest && (
          <>
            <PatientSearchResults
              patients={useCaseQueryResponse?.Patient ?? []}
              originalRequest={originalRequest}
              queryValueSets={queryValuesets}
              setLoading={setLoading}
              goBack={() => setMode("search")}
              setMode={setMode}
              setUseCaseQueryResponse={setUseCaseQueryResponse}
            />
          </>
        )}

        {/* Use LoadingView component for loading state */}
        <LoadingView loading={loading} />

        {/* Show the customize query view to select and change what is returned in results */}
        {mode === "customize-queries" && (
          <>
            <CustomizeQuery
              useCaseQueryResponse={useCaseQueryResponse}
              queryType={queryType}
              queryValuesets={queryValuesets}
              setQueryValuesets={setQueryValuesets}
              goBack={() => {
                setMode("search");
              }}
            />
          </>
        )}
        <ToastContainer icon={false} />
      </div>
    </>
  );
};

export default Query;
