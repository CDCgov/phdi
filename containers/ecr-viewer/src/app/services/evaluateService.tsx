import { Element } from "fhir/r4";
import { ColumnInfoInput, PathMappings } from "@/app/utils";
import { Button, Table } from "@trussworks/react-uswds";
import classNames from "classnames";
import React, { ReactNode, useState } from "react";
import { evaluateValue } from "./evaluateFhirDataService";

interface BuildRowProps {
  mappings: PathMappings;
  columns: ColumnInfoInput[];
  entry: Element;
}

/**
 * Formats a table based on the provided resources, mappings, columns, and caption.
 * @param resources - An array of FHIR Resources representing the data entries.
 * @param mappings - An object containing the FHIR path mappings.
 * @param columns - An array of objects representing column information.
 *                                      The order of columns in the array determines the order of appearance.
 * @param caption - The caption for the table.
 * @param [fixed] - Optional. Determines whether to fix the width of the table columns. Default is true.
 * @param [outerBorder] - Optional. Determines whether to include an outer border for the table. Default is true.
 * @returns - A formatted table React element.
 */
export const evaluateTable = (
  resources: Element[],
  mappings: PathMappings,
  columns: ColumnInfoInput[],
  caption: string,
  fixed: boolean = true,
  outerBorder: boolean = true,
): React.JSX.Element => {
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
    return (
      <BuildRow
        key={index}
        columns={columns}
        mappings={mappings}
        entry={entry}
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

/**
 * Builds a row for a table based on provided columns, mappings, and entry data.
 * @param props - The properties object containing columns, mappings, and entry data.
 * @param props.columns - An array of column objects defining the structure of the row.
 * @param props.mappings - An object containing mappings for column data.
 * @param props.entry - The data entry object for the row.
 * @returns - The JSX element representing the constructed row.
 */
const BuildRow: React.FC<BuildRowProps> = ({
  columns,
  mappings,
  entry,
}: BuildRowProps) => {
  const [hiddenComment, setHiddenComment] = useState(true);

  let hiddenRows: React.JSX.Element[] = [];
  let rowCells = columns.map((column, index) => {
    let rowCellData: ReactNode;
    if (column?.value) {
      rowCellData = column.value;
    } else if (column?.infoPath) {
      rowCellData = evaluateValue(entry, mappings[column.infoPath]);
    }
    if (rowCellData && column.applyToValue) {
      rowCellData = column.applyToValue(rowCellData);
    } else if (!rowCellData) {
      rowCellData = <span className={"text-italic text-base"}>No data</span>;
    } else if (column.hiddenBaseText) {
      hiddenRows.push(
        <tr hidden={hiddenComment} id={`hidden-comment-${index}`}>
          <td colSpan={columns.length} className={"hideableData"}>
            {rowCellData}
          </td>
        </tr>,
      );
      rowCellData = (
        <Button
          unstyled={true}
          type={"button"}
          onClick={() => setHiddenComment(!hiddenComment)}
          aria-controls={`hidden-comment-${index}`}
          aria-expanded={!hiddenComment}
        >
          {hiddenComment ? "View" : "Hide"} {column.hiddenBaseText}
        </Button>
      );
    }
    return (
      <td key={`row-data-${index}`} className="text-top">
        {rowCellData}
      </td>
    );
  });

  if (hiddenRows) {
    return (
      <React.Fragment>
        <tr>{rowCells}</tr>
        {...hiddenRows}
      </React.Fragment>
    );
  } else {
    return <tr>{rowCells}</tr>;
  }
};
