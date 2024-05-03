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
          <th>Date</th>
          <th>Type</th>
          <th>Interpretation</th>
          <th>Value</th>
          <th>Reference Range</th>
        </tr>
      </thead>
      <tbody>
        {encounters.map((encounter) => (
          <tr key={encounter.id}>
            <td>{encounter?.effectiveDateTime}</td>
            <td>{formatCodeableConcept(encounter.code)}</td>
            <td>
              {encounter?.interpretation && encounter.interpretation.length > 0
                ? formatCodeableConcept(encounter.interpretation[0])
                : ""}
            </td>
            <td>{formatValue(encounter)}</td>
            <td>{formatReferenceRange(encounter)}</td>
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
function formatCodeableConcept(concept: CodeableConcept) {
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

