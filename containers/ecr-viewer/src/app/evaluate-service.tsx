import { evaluate } from "fhirpath";
import { Bundle, CodeableConcept, FhirResource, Quantity } from "fhir/r4";
import { ColumnInfoInput } from "@/app/utils";
import { PathMappings } from "@/app/utils";
import fhirpath_r4_model from "fhirpath/fhir-context/r4";
import { Table } from "@trussworks/react-uswds";
import classNames from "classnames";

/**
 * Formats a table based on the provided resources, mappings, columns, and caption.
 * @param {FhirResource[]} resources - An array of FHIR Resources representing the data entries.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @param {ColumnInfoInput[]} columns - An array of objects representing column information.
 *                                      The order of columns in the array determines the order of appearance.
 * @param {string} caption - The caption for the table.
 * @param {boolean} [outerBorder=true] - Optional. Determines whether to include an outer border for the table. Default is true.
 * @returns {React.JSX.Element} - A formatted table React element.
 */
export const evaluateTable = (
  resources: FhirResource[],
  mappings: PathMappings,
  columns: ColumnInfoInput[],
  caption: string,
  outerBorder: boolean = true,
): React.JSX.Element => {
  let headers = columns.map((column, index) => (
    <th
      key={`${column.columnName}${index}`}
      scope="col"
      className="bg-base-lightest"
    >
      {column.columnName}
    </th>
  ));

  let tableRows = resources.map((entry, index) => {
    let rowCells = columns.map((column, index) => {
      let rowCellData = evaluateValue(entry, mappings[column.infoPath]) || (
        <span className={"text-italic text-base"}>No data</span>
      );
      return (
        <td key={`row-data-${index}`} className="text-top">
          {rowCellData}
        </td>
      );
    });

    return <tr key={`table-row-${index}`}>{rowCells}</tr>;
  });

  return (
    <Table
      fixed={true}
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
 * Evaluates a reference in a FHIR bundle.
 *
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
 *
 * @param {FhirResource} entry - The FHIR resource to evaluate.
 * @param {string} path - The path within the resource to extract the value from.
 * @returns {string} - The evaluated value as a string.
 */
export const evaluateValue = (entry: FhirResource, path: string): string => {
  let originalValue = evaluate(entry, path, undefined, fhirpath_r4_model)[0];
  let value = "";
  if (typeof originalValue === "string") {
    value = originalValue;
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
