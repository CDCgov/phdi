"use client";
import React, { useState } from "react";
import { Table } from "@trussworks/react-uswds";
import { SortButton } from "@/app/components/SortButton";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";
import { toSentenceCase } from "@/app/services/formatService";

const basePath =
  process.env.NODE_ENV === "production" ? process.env.NEXT_PUBLIC_BASEPATH : "";

type EcrTableClientProps = {
  data: EcrDisplay[];
  defaultSort: { columnId: string; direction: string };
  startIndex: number;
  itemsPerPage: number;
};

/**
 *
 * @param props - The properties passed to the component.
 * @param props.data  - The data to be displayed in the table.
 * @param props.defaultSort - The default sort column and direction.
 * @param props.startIndex  - The index of the first item to be displayed.
 * @param props.itemsPerPage - The number of items to be displayed in the table.
 * @returns - The JSX element representing the eCR table.
 */
export const EcrTableClient: React.FC<EcrTableClientProps> = ({
  data,
  defaultSort,
  startIndex,
  itemsPerPage,
}) => {
  const [sortedData, setSortedData] = useState(data);
  const [sortConfig, setSortConfig] = useState(defaultSort);

  const handleSort = async (columnId) => {
    // Toggle sorting direction
    const direction = sortConfig.direction === "asc" ? "desc" : "asc";

    // Update sort state
    setSortConfig({ columnId, direction });

    // Fetch new sorted data from an API route or directly from server
    // @todo: Add sort to query call with sortConfig
    const sortedData = await listEcrData(startIndex, itemsPerPage);

    // Update the sorted data
    setSortedData(sortedData);
  };

  const header = [
    {
      id: "patient",
      value: "Patient",
      className: "minw-20",
      dataSortable: true,
      sortDirection: "",
    },
    {
      id: "received-date",
      value: "Received Date",
      className: "minw-1605",
      dataSortable: true,
      sortDirection: "",
    },
    {
      id: "encounter-date",
      value: "Encounter Date",
      className: "minw-1705",
      dataSortable: true,
      sortDirection: "",
    },
    {
      id: "reportable-condition",
      value: "Reportable Condition",
      className: "minw-2305",
      dataSortable: false,
      sortDirection: "",
    },
    {
      id: "rule-summary",
      value: "RCKMS Rule Summary",
      className: "minw-23",
      dataSortable: false,
      sortDirection: "",
    },
  ];
  return (
    <div className="ecr-library-wrapper width-full overflow-auto">
      <Table
        bordered={false}
        fullWidth={true}
        striped={true}
        fixed={true}
        className={"table-ecr-library margin-0"}
        data-testid="table"
      >
        <thead className={"position-sticky top-0"}>
          <tr>
            {header.map((column) =>
              column.sortDirection ? (
                <th
                  id={`${column.id}-header`}
                  key={`${column.value}`}
                  scope="col"
                  role="columnheader"
                  className={column.className}
                  data-sortable={column.dataSortable}
                  aria-sort={getAriaSortValue(
                    column.sortDirection,
                    column.value,
                  )}
                >
                  {column.value}
                  <div>
                    <SortButton
                      columnName={column.id}
                      columnSortDirection={column.sortDirection}
                      className={"sortable-desc-column"}
                      onClick={() => handleSort(column.id)}
                    ></SortButton>
                  </div>
                </th>
              ) : (
                <th
                  id={`${column.id}-header`}
                  key={`${column.value}`}
                  scope="col"
                  role="columnheader"
                  className={column.className}
                >
                  {column.value}
                  {column.dataSortable ? (
                    <div>
                      <SortButton
                        columnName={column.id}
                        columnSortDirection={column.sortDirection}
                        className={"sortable-column"}
                        onClick={() => handleSort(column.id)}
                      ></SortButton>
                    </div>
                  ) : null}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>{renderListEcrTableData(sortedData)}</tbody>
      </Table>
      <div
        class="usa-sr-only usa-table__announcement-region"
        aria-live="polite"
      ></div>
    </div>
  );
};

type AriaSortType = "none" | "ascending" | "descending" | "other";

const getAriaSortValue = (
  sortDirection: string,
  columnValue: string,
): AriaSortType => {
  console.log(columnValue);
  if (sortDirection !== "") {
    console.log("sorted");
    return sortDirection === "asc" ? "ascending" : "descending";
  }
  console.log("unsorted");
  return "none";
};

/**
 * Renders table rows given a list of eCRs. Each row contains an eCR ID linked to its
 * individual eCR viewer page and the stor    ed date.
 * @param listFhirData - The list of eCRs to render.
 * @returns An array of JSX table row elements representing the list of eCRs.
 */
const renderListEcrTableData = (listFhirData: EcrDisplay[]) => {
  return listFhirData.map((item, index) => {
    return formatRow(item, index);
  });
};

/**
 * Formats a single row of the eCR table.
 * @param item - The eCR data to be formatted.
 * @param index - The index of the eCR data in the list.
 * @returns A JSX table row element representing the eCR data.
 */
const formatRow = (item: EcrDisplay, index: number) => {
  let patient_first_name = toSentenceCase(item.patient_first_name);
  let patient_last_name = toSentenceCase(item.patient_last_name);
  let createDateObj = new Date(item.date_created);
  let createDateDate = formatDate(createDateObj);
  let createDateTime = formatTime(createDateObj);
  let patientReportDateObj = new Date(item.patient_report_date);
  let patientReportDate = formatDate(patientReportDateObj);
  let patientReportTime = formatTime(patientReportDateObj);

  return (
    <tr key={`table-row-${index}`}>
      <td>
        <a href={`${basePath}/view-data?id=${item.ecrId}`}>
          {patient_first_name} {patient_last_name}
        </a>
        <br />
        <div>{"DOB: " + item.patient_date_of_birth || ""}</div>
      </td>
      <td>
        {createDateDate}
        <br />
        {createDateTime}
      </td>
      <td>
        {patientReportDate}
        <br />
        {patientReportTime}
      </td>
      <td>{item.reportable_condition}</td>
      <td>{item.rule_summary}</td>
    </tr>
  );
};

/**
 * Formats a date object to a string in the format MM/DD/YYYY.
 * @param date - The date object to be formatted.
 * @returns A string in the format MM/DD/YYYY.
 */
const formatDate = (date: Date) => {
  return date.toLocaleDateString("en-US");
};

/**
 * Formats a date object to a string in the format HH:MM AM/PM.
 * @param date - The date object to be formatted.
 * @returns A string in the format HH:MM AM/PM.
 */
const formatTime = (date: Date) => {
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? "PM" : "AM";

  hours = hours % 12;
  hours = hours ? hours : 12;

  const minutesStr = minutes < 10 ? `0${minutes}` : minutes;

  return `${hours}:${minutesStr} ${ampm}`;
};
