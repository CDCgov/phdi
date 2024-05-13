import React from "react";
import { Table } from "@trussworks/react-uswds";
import { DiagnosticReport } from "fhir/r4";
import { formatCodeableConcept, formatDate } from "../../format-service";

/**
 * The props for the DiagnosticReportTable component.
 */
export interface DiagnosticReportTableProps {
  diagnosticReports: DiagnosticReport[];
}

/**
 * Displays a table of data from array of DiagnosticReport resources.
 * @param props - DiagnosticReport table props.
 * @param props.diagnosticReports - The array of DiagnosticReport resources.
 * @returns - The DiagnosticReportTable component.
 */
const DiagnosticReportTable: React.FC<DiagnosticReportTableProps> = ({
  diagnosticReports,
}) => {
  return (
    <Table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Code</th>
        </tr>
      </thead>
      <tbody>
        {diagnosticReports.map((diagnosticReport) => (
          <tr key={diagnosticReport.id}>
            <td>{formatDate(diagnosticReport?.effectiveDateTime)}</td>
            <td>{formatCodeableConcept(diagnosticReport.code)}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default DiagnosticReportTable;
