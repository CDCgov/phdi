import React, { useEffect } from "react";
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
  useCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import { Mode } from "../page";

/**
 * The props for the MultiplePatientSearchResults component.
 */
export interface MultiplePatientSearchResultsProps {
  patients: Patient[];
  originalRequest: UseCaseQueryRequest;
  setUseCaseQueryResponse: (useCaseQueryResponse: UseCaseQueryResponse) => void;
  setMode: (mode: Mode) => void;
  setLoading: (loading: boolean) => void;
}

/**
 * Displays multiple patient search results in a table.
 * @param root0 - MultiplePatientSearchResults props.
 * @param root0.patients - The array of Patient resources.
 * @param root0.originalRequest - The original request object.
 * @param root0.setUseCaseQueryResponse - The function to set the use case query response.
 * @param root0.setMode - The function to set the mode.
 * @param root0.setLoading - The function to set the loading state.
 * @returns - The MultiplePatientSearchResults component.
 */
const MultiplePatientSearchResults: React.FC<
  MultiplePatientSearchResultsProps
> = ({
  patients,
  originalRequest,
  setUseCaseQueryResponse,
  setMode,
  setLoading,
}) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
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
                        setUseCaseQueryResponse,
                        setMode,
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
        <a href="#" onClick={() => setMode("search")}>
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
    <>The following records match by the values provided for </>,
  ];
  let comma = ", ";
  if (searchElements.length <= 2) {
    comma = " ";
  }
  for (let i = 0; i < searchElements.length; i++) {
    if (i === searchElements.length - 1) {
      if (searchElements.length > 1) {
        noteParts.push(<>and </>);
      }
      comma = "";
    }
    switch (searchElements[i]) {
      case "first_name":
        noteParts.push(
          <strong style={{ fontWeight: 550 }}>{"First Name" + comma}</strong>,
        );
        break;
      case "last_name":
        noteParts.push(
          <strong style={{ fontWeight: 550 }}>{"Last Name" + comma}</strong>,
        );
        break;
      case "dob":
        noteParts.push(
          <strong style={{ fontWeight: 550 }}>{"DOB" + comma}</strong>,
        );
        break;
    }
  }
  noteParts.push(<>:</>);
  return <p className="font-sans-lg text-light">{noteParts}</p>;
}

/**
 * When a user clicks on a record, this function queries the FHIR server for the record
 * and sets the mode to "results" thereby displaying the query results for that patient.
 * @param patients - The array of patients.
 * @param index - The index of the patient to view.
 * @param originalRequest - The original request object.
 * @param setUseCaseQueryResponse - The function to set the use case query response.
 * @param setMode - The function to set the mode.
 * @param setLoading - The function to set the loading state.
 */
async function viewRecord(
  patients: Patient[],
  index: number,
  originalRequest: UseCaseQueryRequest,
  setUseCaseQueryResponse: (useCaseQueryResponse: UseCaseQueryResponse) => void,
  setMode: (mode: Mode) => void,
  setLoading: (loading: boolean) => void,
): Promise<void> {
  setLoading(true);
  const queryResponse = await useCaseQuery(originalRequest, {
    Patient: [patients[index]],
  });
  setUseCaseQueryResponse(queryResponse);
  setMode("results");
  setLoading(false);
}
