import Table from "../../designSystem/Table";
import { Patient } from "fhir/r4";
import {
  formatAddress,
  formatContact,
  formatMRN,
  formatName,
} from "@/app/format-service";

type PatientSeacrchResultsTableProps = {
  patients: Patient[];
  handlePatientSelect: (patient: Patient) => void;
};

/**
 * Patient search results table for users to select which patient they want to
 * include in their query
 * @param param0 - props
 * @param param0.patients - Patient[] from the FHIR spec to display as rows
 * @param param0.handlePatientSelect - state setter function to redirect
 * to the results view
 * @returns The patient search results view
 */
const PatientSearchResultsTable: React.FC<PatientSeacrchResultsTableProps> = ({
  patients,
  handlePatientSelect: setPatientForQueryResponse,
}) => {
  return (
    <>
      <h1 className="font-sans-2xl text-bold margin-top-205">
        Select a patient
      </h1>
      <p className="font-sans-lg text-light">
        The following records match your search. Select a patient to continue.
      </p>
      <Table className="margin-top-5">
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
            <tr
              key={patient.id}
              className="tableRowWithHover tableRowWithHover_clickable"
              onClick={() => setPatientForQueryResponse(patient)}
            >
              <td>{formatName(patient.name ?? [])}</td>
              <td>{patient.birthDate ?? ""}</td>
              <td>{formatContact(patient.telecom ?? [])}</td>
              <td>{formatAddress(patient.address ?? [])}</td>
              <td>{formatMRN(patient.identifier ?? [])}</td>
              <td>
                <a
                  href="#"
                  className="unchanged-color-on-visit"
                  onClick={() => setPatientForQueryResponse(patient)}
                >
                  Select patient
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
};

export default PatientSearchResultsTable;
