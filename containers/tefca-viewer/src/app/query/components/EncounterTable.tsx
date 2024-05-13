import React from "react";
import { Table } from "@trussworks/react-uswds";
import { Encounter } from "fhir/r4";
import { formatCodeableConcept, formatDate } from "../../format-service";

/**
 * The props for the EncounterTable component.
 */
export interface EncounterTableProps {
  encounters: Encounter[];
}

/**
 * Displays a table of data from array of Encounter resources.
 * @param root0 - Encounter table props.
 * @param root0.encounters - The array of Encounter resources.
 * @returns - The EncounterTable component.
 */
const EncounterTable: React.FC<EncounterTableProps> = ({
  encounters: encounters,
}) => {
  return (
    <Table>
      <thead>
        <tr>
          <th>Visit Reason</th>
          <th>Clinic Type</th>
          <th>Service Provider</th>
          <th>Encounter Status</th>
          <th>Encounter Start</th>
          <th>Encounter End</th>
        </tr>
      </thead>
      <tbody>
        {encounters.map((encounter) => (
          <tr key={encounter.id}>
            <td>{formatCodeableConcept(encounter?.reasonCode?.[0])} </td>
            <td>
              {formatCodeableConcept(encounter?.class)} <br></br>
              {encounter?.serviceType
                ? formatCodeableConcept(encounter.serviceType)
                : ""}
            </td>
            <td>{encounter?.serviceProvider?.display}</td>
            <td>{encounter?.status}</td>
            <td>{formatDate(encounter?.period?.start)}</td>
            <td>{formatDate(encounter?.period?.end)}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};
export default EncounterTable;
