import React, { Fragment, useEffect, useState } from "react";
import { Table } from "@trussworks/react-uswds";
import { Patient } from "fhir/r4";
import {
  formatName,
  formatAddress,
  formatContact,
  formatMRN,
} from "../../format-service";
import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import ResultsView from "./ResultsView";

/**
 * The props for the MultiplePatientSearchResults component.
 */
export interface MultiplePatientSearchResultsProps {
  patients: Patient[];
  originalRequest: UseCaseQueryRequest;
  setLoading: (loading: boolean) => void;
  goBack: () => void;
}

/**
 * Displays multiple patient search results in a table.
 * @param root0 - MultiplePatientSearchResults props.
 * @param root0.patients - The array of Patient resources.
 * @param root0.originalRequest - The original request object.
 * @param root0.setLoading - The function to set the loading state.
 * @param root0.goBack - The function to go back to the previous page.
 * @returns - The MultiplePatientSearchResults component.
 */
const MultiplePatientSearchResults: React.FC<
  MultiplePatientSearchResultsProps
> = ({ patients, originalRequest, setLoading, goBack }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  // Determines whether to show the results of a single patient (ResultsView) or
  // go back to the multiple patients view (below)
  const [singleUseCaseQueryResponse, setSingleUseCaseQueryResponse] =
    useState<UseCaseQueryResponse>();

  if (singleUseCaseQueryResponse) {
    // If a single patient is selected, show the button for returning to the search results
    // & take user back to the search results by setting the singleUseCaseQueryResponse to undefined
    return (
      <ResultsView
        useCaseQueryResponse={singleUseCaseQueryResponse}
        goBack={() => setSingleUseCaseQueryResponse(undefined)}
        backLabel="Return to search results"
      />
    );
  }

  return (
    <>
      <div className="multiple-patient-search-results">
        <h1 className="font-sans-2xl text-bold">Multiple Records Found</h1>
        {searchResultsNote(originalRequest)}
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>DOB</th>
              <th>Contact</th>
              <th>Address</th>
              <th>MRN</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((patient, index) => (
              <tr key={patient.id}>
                <td>{formatName(patient.name ?? [])}</td>
                <td>{patient.birthDate ?? ""}</td>
                <td>{formatContact(patient.telecom ?? [])}</td>
                <td>{formatAddress(patient.address ?? [])}</td>
                <td>{formatMRN(patient.identifier ?? [])}</td>
                <td>
                  <a
                    href="#"
                    onClick={() =>
                      viewRecord(
                        patients,
                        index,
                        originalRequest,
                        setSingleUseCaseQueryResponse,
                        setLoading,
                      )
                    }
                  >
                    View Record
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
        <h3>Not seeing what you are looking for?</h3>
        <a href="#" onClick={() => goBack()}>
          Return to patient search
        </a>
      </div>
    </>
  );
};

export default MultiplePatientSearchResults;

/**
 * Creates a note about which fields the search results match on.
 * @param request - The request object.
 * @returns - The JSX element for the note.
 */
function searchResultsNote(request: UseCaseQueryRequest): JSX.Element {
  let searchElements = Object.entries(request).map(([key, value]) => {
    if (value && value !== "" && key !== "use_case" && key !== "fhir_server") {
      return key;
    }
  });

  searchElements = searchElements.filter((element) => element !== undefined);

  let noteParts = [
    <Fragment key="start">
      The following records match by the values provided for{" "}
    </Fragment>,
  ];
  let comma = ", ";
  if (searchElements.length <= 2) {
    comma = " ";
  }
  for (let i = 0; i < searchElements.length; i++) {
    if (i === searchElements.length - 1) {
      if (searchElements.length > 1) {
        noteParts.push(<Fragment key="and">and </Fragment>);
      }
      comma = "";
    }
    switch (searchElements[i]) {
      case "first_name":
        noteParts.push(
          <strong key={searchElements[i]} style={{ fontWeight: 550 }}>
            {"First Name" + comma}
          </strong>,
        );
        break;
      case "last_name":
        noteParts.push(
          <strong key={searchElements[i]} style={{ fontWeight: 550 }}>
            {"Last Name" + comma}
          </strong>,
        );
        break;
      case "dob":
        noteParts.push(
          <strong key={searchElements[i]} style={{ fontWeight: 550 }}>
            {"DOB" + comma}
          </strong>,
        );
        break;
    }
  }
  noteParts.push(<Fragment key=":">:</Fragment>);
  return <p className="font-sans-lg text-light">{noteParts}</p>;
}

/**
 * When a user clicks on a record, this function queries the FHIR server for the record
 * and sets the mode to "results" thereby displaying the query results for that patient.
 * @param patients - The array of patients.
 * @param index - The index of the patient to view.
 * @param originalRequest - The original request object.
 * @param setUseCaseQueryResponse - The function to set the use case query response.
 * @param setLoading - The function to set the loading state.
 */
async function viewRecord(
  patients: Patient[],
  index: number,
  originalRequest: UseCaseQueryRequest,
  setUseCaseQueryResponse: (UseCaseQueryResponse: UseCaseQueryResponse) => void,
  setLoading: (loading: boolean) => void,
): Promise<void> {
  setLoading(true);
  const queryResponse = await UseCaseQuery(originalRequest, {
    Patient: [patients[index]],
  });
  setUseCaseQueryResponse(queryResponse);

  setLoading(false);
}
