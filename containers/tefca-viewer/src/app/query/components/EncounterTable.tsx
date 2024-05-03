import React from "react";
import { Table } from "@trussworks/react-uswds";
import { Encounter, CodeableConcept } from "fhir/r4";

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
            <td>{encounter?.period?.start}</td>
            <td>{encounter?.period?.end}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};
export default EncounterTable;

/**
 * Formats a CodeableConcept object for display. If the object has a coding array,
 * the first coding object is used.
 * @param concept - The CodeableConcept object.
 * @returns The CodeableConcept data formatted for
 * display.
 */
function formatCodeableConcept(concept: CodeableConcept | undefined) {
  if (!concept) {
    return "";
  }
  if (!concept.coding || concept.coding.length === 0) {
    return concept.text || "";
  }
  const coding = concept.coding[0];
  return (
    <>
      {" "}
      {coding.display} <br /> {coding.code} <br /> {coding.system}{" "}
    </>
  );
}
