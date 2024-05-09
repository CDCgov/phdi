import React from "react";
import { Table } from "@trussworks/react-uswds";
import { Patient } from "fhir/r4";
import {
  formatName,
  formatAddress,
  formatContact,
  formatIdentifier,
} from "../../format-service";

/**
 * The props for the MultiplePatientSearchResults component.
 */
export interface MultiplePatientSearchResultsProps {
  patients: Patient[];
}

/**
 * Displays multiple patient search results in a table.
 * @param root0 - MultiplePatientSearchResults props.
 * @param root0.patients - The array of Patient resources.
 * @returns - The MultiplePatientSearchResults component.
 */
const MultiplePatientSearchResults: React.FC<
  MultiplePatientSearchResultsProps
> = ({ patients }) => {
  return (
    <>
      <h2>Multiple Patient Records Found</h2>
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
          {patients.map((patient) => (
            <tr key={patient.id}>
              <td>{formatName(patient.name ?? [])}</td>
              <td>{patient.birthDate ?? ""}</td>
              <td>{formatContact(patient.telecom ?? [])}</td>
              <td>{formatAddress(patient.address ?? [])}</td>
              <td>{formatIdentifier(patient.identifier ?? [])}</td>
              <td>
                <a href={`/patient/${patient.id}`}>View Record</a>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};

export default MultiplePatientSearchResults;
