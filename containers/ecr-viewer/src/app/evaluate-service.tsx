import { evaluate } from "fhirpath";
import { Bundle, CodeableConcept, FhirResource, Quantity } from "fhir/r4";
import { toSentenceCase } from "./format-service";
import { ColumnInfoInput, PathMappings } from "@/app/utils";
import fhirpath_r4_model from "fhirpath/fhir-context/r4";
import { Button, Table } from "@trussworks/react-uswds";
import classNames from "classnames";
import React, { useState } from "react";

interface BuildRowProps {
  mappings: PathMappings;
  columns: ColumnInfoInput[];
  entry: FhirResource;
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
  resources: FhirResource[],
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
    let rowCellData: any;
    if (column?.value) {
      rowCellData = column.value;
    } else if (column?.infoPath) {
      rowCellData = evaluateValue(entry, mappings[column.infoPath]);
    }
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
        {column.sentenceCase ? toSentenceCase(rowCellData) : rowCellData}
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

/**
 * Evaluates a reference in a FHIR bundle.
 * @param fhirBundle - The FHIR bundle containing resources.
 * @param mappings - Path mappings for resolving references.
 * @param ref - The reference string (e.g., "Patient/123").
 * @returns The FHIR Resource or undefined if not found.
 */
export const evaluateReference = (
  fhirBundle: Bundle,
  mappings: PathMappings,
  ref: string,
) => {
  const [resourceType, id] = ref.split("/");
  return evaluate(fhirBundle, mappings.resolve, {
    resourceType,
    id,
  })[0];
};

/**
 * Evaluates the FHIR path and returns the appropriate string value. Supports choice elements
 * @param entry - The FHIR resource to evaluate.
 * @param path - The path within the resource to extract the value from.
 * @returns - The evaluated value as a string.
 */
export const evaluateValue = (entry: FhirResource, path: string): string => {
  let originalValue = evaluate(entry, path, undefined, fhirpath_r4_model)[0];
  let value = "";
  if (typeof originalValue === "string" || typeof originalValue === "number") {
    value = originalValue.toString();
  } else if (originalValue?.__path__ === "Quantity") {
    const data = originalValue as Quantity;
    let unit = data.unit;
    const firstLetterRegex = /^[a-z]/i;
    if (unit?.match(firstLetterRegex)) {
      unit = " " + unit;
    }
    value = `${data.value ?? ""}${unit ?? ""}`;
  } else if (originalValue?.__path__ === "CodeableConcept") {
    const data = originalValue as CodeableConcept;
    value = data.coding?.[0].display || data.text || "";
  } else if (typeof originalValue === "object") {
    console.log(`Not implemented for ${originalValue.__path__}`);
  }
  return value.trim();
};
