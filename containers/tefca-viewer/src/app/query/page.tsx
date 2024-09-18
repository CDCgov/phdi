"use client";
import React, { Suspense, useEffect, useState } from "react";
import { UseCaseQueryResponse, UseCaseQueryRequest } from "../query-service";
import ResultsView from "./components/ResultsView";
import MultiplePatientSearchResults from "./components/MultiplePatientSearchResults";
import SearchForm from "./components/SearchForm";
import NoPatientsFound from "./components/NoPatientsFound";
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
import StepIndicator, {
  CUSTOMIZE_QUERY_STEPS,
} from "./stepIndicator/StepIndicator";
import { Alert } from "@trussworks/react-uswds";
import { alertBannerMap } from "./components/DisclaimerAlerts";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [useCase, setUseCase] = useState<USE_CASES>("" as USE_CASES);
  const [queryType, setQueryType] = useState<string>("");
  const [queryValuesets, setQueryValuesets] = useState<ValueSetItem[]>(
    [] as ValueSetItem[]
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
    <div>
      {Object.keys(alertBannerMap).includes(mode) &&
        alertBannerMap[mode as Mode]}

      {Object.keys(CUSTOMIZE_QUERY_STEPS).includes(mode) && (
        <StepIndicator headingLevel="h4" curStep={mode} />
      )}
      {mode === "search" && (
        <Suspense fallback="...Loading">
          <SearchForm
            useCase={useCase}
            setUseCase={setUseCase}
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
  );
};

export default Query;
