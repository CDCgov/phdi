import React from "react";
import { Table } from "@trussworks/react-uswds";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";
import { toSentenceCase } from "@/app/services/formatService";
import { SortButton } from "@/app/components/SortButton";

const basePath =
  process.env.NODE_ENV === "production" ? process.env.NEXT_PUBLIC_BASEPATH : "";

/**
 * eCR Table
 * @param props - The properties passed to the component.
 * @param props.currentPage - The current page to be displayed
 * @param props.itemsPerPage - The number of items to be displayed in the table
 * @returns - eCR Table element
 */
const EcrTable = async ({
  currentPage,
  itemsPerPage,
}: {
  currentPage: number;
  itemsPerPage: number;
}) => {
  const renderPage = async (pageNumber: number) => {
    const startIndex = (pageNumber - 1) * itemsPerPage;
    const pageData = await listEcrData(startIndex, itemsPerPage);
    return renderListEcrTableData(pageData);
  };

  let currentSortedColumnId = "";

  const handleSort = (columnnId: string): void => {
    const columnToUnSort = header.find(
      (item) => item.id === currentSortedColumnId,
    );
    const columnToSort = header.find((item) => item.id === columnnId);
    console.log("handle sort");
    console.log(columnToSort);
    console.log(columnToUnSort);
    if (columnToUnSort) {
      columnToUnSort.sortDirection = "";
    }

    if (columnToSort && columnToSort!.sortDirection === "") {
      columnToSort.sortDirection = "asc";
    } else if (columnToSort && columnToSort!.sortDirection === "desc") {
      columnToSort.sortDirection = "asc";
    }
    currentSortedColumnId = columnnId;
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
                      currentSortedColumnId={currentSortedColumnId}
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
                        currentSortedColumnId={currentSortedColumnId}
                      ></SortButton>
                    </div>
                  ) : null}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>{await renderPage(currentPage)}</tbody>
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
 * individual eCR viewer page and the stored date.
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

export default EcrTable;
