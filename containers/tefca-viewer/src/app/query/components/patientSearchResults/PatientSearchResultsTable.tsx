import Table from "../../designSystem/Table";
import { Patient } from "fhir/r4";
import Backlink from "../backLink/Backlink";
import {
  formatAddress,
  formatContact,
  formatMRN,
  formatName,
} from "@/app/format-service";

type PatientSeacrchResultsTableProps = {
  patients: Patient[];
  setPatientForQueryResponse: (patient: Patient) => void;
};

const PatientSearchResultsTable: React.FC<PatientSeacrchResultsTableProps> = ({
  patients,
  setPatientForQueryResponse,
}) => {
  return (
    <>
      <div className="multiple-patient-search-results">
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
                <td>{formatMRN(patient.identifier ?? [])}</td>
                <td>
                  <a
                    href="#"
                    onClick={() => setPatientForQueryResponse(patient)}
                  >
                    View Record
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
    </>
  );
};

export default PatientSearchResultsTable;
