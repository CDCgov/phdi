"use client";
import React, { ReactNode, useState } from "react";
import { Button } from "@trussworks/react-uswds";
import { ColumnInfoInput } from "@/app/utils";

type ClientColumnInfoInput = Omit<ColumnInfoInput, "applyToValue">;

interface BuildRowProps {
  columns: ClientColumnInfoInput[];
  rowValues: ReactNode[];
}

/**
 * Builds a row for a table based on provided columns, mappings, and entry data.
 * @param props - The properties object containing columns, mappings, and entry data.
 * @param props.columns - An array of column objects defining the structure of the row.
 * @param props.rowValues - Values to be inserted into the row
 * @returns - The JSX element representing the constructed row.
 */
const BuildRow: React.FC<BuildRowProps> = ({
  columns,
  rowValues,
}: BuildRowProps) => {
  const [hiddenComment, setHiddenComment] = useState(true);

  let hiddenRows: React.JSX.Element[] = [];
  let rowCells = columns.map((column, index) => {
    let rowCellData = rowValues[index];
    if (!rowCellData) {
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

export default BuildRow;
