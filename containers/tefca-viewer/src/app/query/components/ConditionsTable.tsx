import React from "react";
import { Table } from "@trussworks/react-uswds";
import { Condition } from "fhir/r4";
import { formatCodeableConcept, formatDate } from "../../format-service";

/**
 * The props for the ConditionTable component.
 */
export interface ConditionTableProps {
  conditions: Condition[];
}

/**
 * Displays a table of data from array of Condition resources.
 * @param props - Condition table props.
 * @param props.conditions - The array of Condition resources.
 * @returns - The ConditionTable component.
 */
const ConditionsTable: React.FC<ConditionTableProps> = ({ conditions }) => {
  return (
    <Table>
      <thead>
        <tr>
          <th>Condition</th>
          <th>Status</th>
          <th>Onset</th>
          <th>Resolution</th>
        </tr>
      </thead>
      <tbody>
        {conditions.map((condition) => (
          <tr key={condition.id}>
            <td>{formatCodeableConcept(condition.code ?? {})}</td>
            <td>{formatCodeableConcept(condition.clinicalStatus ?? {})}</td>
            <td>{formatDate(condition.onsetDateTime)}</td>
            <td>{formatDate(condition.abatementDateTime)}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ConditionsTable;
