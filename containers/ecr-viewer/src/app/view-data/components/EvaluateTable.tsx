import { Element } from "fhir/r4";
import { ColumnInfoInput, PathMappings } from "@/app/utils";
import { Table } from "@trussworks/react-uswds";
import classNames from "classnames";
import React, { ReactNode } from "react";
import { evaluateValue } from "../../services/evaluateFhirDataService";
import BuildRow from "@/app/view-data/components/BuildRow";

interface TableProps {
  resources: Element[];
  mappings: PathMappings;
  columns: ColumnInfoInput[];
  caption?: string;
  fixed?: boolean;
  outerBorder?: boolean;
}
interface EvaluateRowProps {
  fhirElement: Element;
  mappings: PathMappings;
  column: ColumnInfoInput;
}
/**
 * Formats a table based on the provided resources, mappings, columns, and caption.
 * @param props - The properties for configuring the table.
 * @param props.resources - An array of FHIR Resources representing the data entries.
 * @param props.mappings - An object containing the FHIR path mappings.
 * @param props.columns - An array of objects representing column information. The order of columns in the array determines the order of appearance.
 * @param props.caption - The caption for the table.
 * @param props.fixed - Determines whether to fix the width of the table columns. Default is true.
 * @param props.outerBorder - Determines whether to include an outer border for the table. Default is true
 * @returns - A formatted table React element.
 */
const EvaluateTable = ({
  resources,
  mappings,
  columns,
  caption,
  fixed = true,
  outerBorder = true,
}: TableProps): React.JSX.Element => {
  let headers = columns.map((column, index) => (
    <th
      key={`${column.columnName}${index}`}
      scope="col"
      className="tableHeader"
    >
      {column.columnName}
    </th>
  ));

  let tableRows = resources.map((entry, index) => {
    const rowValues = columns.map((column) => {
      return (
        <RowData fhirElement={entry} mappings={mappings} column={column} />
      );
    });
    return (
      <BuildRow
        key={index}
        columns={columns.map(
          ({ applyToValue: _applyToValue, ...everythingElse }) =>
            everythingElse,
        )}
        rowValues={rowValues}
      />
    );
  });

  return (
    <Table
      fixed={fixed}
      bordered={false}
      fullWidth={true}
      caption={caption}
      className={classNames("table-caption-margin margin-y-0", {
        "border-top border-left border-right": outerBorder,
      })}
      data-testid="table"
    >
      <thead>
        <tr>{headers}</tr>
      </thead>
      <tbody>{tableRows}</tbody>
    </Table>
  );
};

const RowData = ({ column, mappings, fhirElement }: EvaluateRowProps) => {
  let rowData: ReactNode;
  if (column?.value) {
    rowData = column.value;
  } else if (column?.infoPath) {
    rowData = evaluateValue(fhirElement, mappings[column.infoPath]);
  }

  if (rowData && column.applyToValue) {
    rowData = column.applyToValue(rowData);
  }

  return rowData;
};

export default EvaluateTable;
