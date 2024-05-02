import React from "react";
import { Table } from "@trussworks/react-uswds";
import { Observation, CodeableConcept } from "fhir/r4";

/**
 * The props for the ObservationTable component.
 */
export interface ObservationTableProps {
  observations: Observation[];
}

/**
 * Displays a table of data from array of Observations resources.
 * @param root0 - Observation table props.
 * @param root0.observations - The array of Observation resources.
 * @returns - The ObservationTable component.
 */
const ObservationTable: React.FC<ObservationTableProps> = ({
  observations,
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
        {observations.map((obs) => (
          <tr key={obs.id}>
            <td>{obs?.effectiveDateTime}</td>
            <td>{formatCodeableConcept(obs.code)}</td>
            <td>
              {obs?.interpretation && obs.interpretation.length > 0
                ? formatCodeableConcept(obs.interpretation[0])
                : ""}
            </td>
            <td>{formatValue(obs)}</td>
            <td>{formatReferenceRange(obs)}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};
export default ObservationTable;

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

/**
 * Formats the value of an Observation object for display.
 * @param obs - The Observation object.
 * @returns The value of the Observation object formatted for display.
 */
function formatValue(obs: Observation) {
  if (obs.valueCodeableConcept) {
    return formatCodeableConcept(obs.valueCodeableConcept);
  } else if (obs.valueQuantity) {
    return [obs.valueQuantity.value, obs.valueQuantity.unit].join(" ");
  } else if (obs.valueString) {
    return obs.valueString;
  }
  return "";
}

/**
 * Formats the reference range of an Observation object for display.
 * @param obs - The Observation object.
 * @returns The reference range of the Observation object formatted for display.
 */
function formatReferenceRange(obs: Observation) {
  if (!obs.referenceRange || obs.referenceRange.length === 0) {
    return "";
  }
  const range = obs.referenceRange[0];

  if (range.high || range.low) {
    return (
      <>
        {["HIGH:", range.high?.value, range.high?.unit].join(" ")} <br />{" "}
        {["LOW:", range.low?.value, range.low?.unit].join(" ")}
      </>
    );
  } else if (range.text) {
    return range.text;
  }
  return "";
}
