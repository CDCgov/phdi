"use client";

import { Label, Select, Table } from "@trussworks/react-uswds";
import React, { useEffect, useState } from "react";
import { Pagination } from "@trussworks/react-uswds";
import { EcrDisplay } from "@/app/api/services/listEcrDataService";

interface ListEcrViewerProps {
  listFhirData: EcrDisplay[];
}

interface UserPreferences {
  itemsPerPage: number;
}

const defaultPreferences = {
  itemsPerPage: 25,
};

/**
 * Renders a list of eCR data with viewer.
 * @param listFhirData - The list of eCRs to render.
 * @param listFhirData.listFhirData The array of eCRs IDs and date values.
 * @returns The JSX element (table) representing the rendered list of eCRs.
 */
export default function ListECRViewer({
  listFhirData,
}: ListEcrViewerProps): React.JSX.Element {
  const header = [
    { value: "Patient", className: "minw-20" },
    { value: "Received Date", className: "minw-1605" },
    { value: "Encounter Date", className: "minw-1705" },
    { value: "Reportable Condition", className: "minw-2305" },
    { value: "RCKMS Rule Summary", className: "minw-23" },
  ];
  const [currentPage, setCurrentPage] = useState(1);
  const [userPreferences, setUserPreferences] =
    useState<UserPreferences>(defaultPreferences);

  useEffect(() => {
    const userPreferencesString = localStorage.getItem("userPreferences");
    if (userPreferencesString) {
      setUserPreferences(JSON.parse(userPreferencesString));
    }
  }, []);

  const totalPages = Math.ceil(
    listFhirData.length / userPreferences.itemsPerPage,
  );

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
    renderPage(pageNumber);
  };

  const renderPage = (pageNumber: number) => {
    const startIndex = (pageNumber - 1) * userPreferences.itemsPerPage;
    const endIndex = startIndex + userPreferences.itemsPerPage;
    const pageData = listFhirData.slice(startIndex, endIndex);
    return renderListEcrTableData(pageData);
  };

  return (
    <div className="main-container height-full flex-column flex-align-center">
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
              {header.map((column) => (
                <th
                  key={`${column.value}`}
                  scope="col"
                  className={column.className}
                >
                  {column.value}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>{renderPage(currentPage)}</tbody>
        </Table>
      </div>
      <div className="pagination-bar width-full padding-x-3 padding-y-105 flex-align-self-stretch display-flex flex-align-center">
        <div className={"flex-1"}>
          Showing {"current"} of {totalPages} eCRs
        </div>
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pathname={""}
          onClickNext={() => handlePageChange(currentPage + 1)}
          onClickPrevious={() => handlePageChange(currentPage - 1)}
          onClickPageNumber={(
            _event: React.MouseEvent<HTMLButtonElement>,
            page: number,
          ) => {
            handlePageChange(page);
          }}
          className={"flex-1"}
        />
        <div
          className={"display-flex flex-align-center flex-1 flex-justify-end"}
        >
          <Label
            htmlFor="input-select"
            className={"margin-top-0 margin-right-1025"}
          >
            eCRs per page
          </Label>
          <Select
            id="input-select"
            name="input-select"
            value={userPreferences.itemsPerPage}
            className={"styled width-11075 margin-top-0"}
            onChange={(e) => {
              const updatedUserPreferences: UserPreferences = {
                ...userPreferences,
                itemsPerPage: +e.target.value,
              };
              setUserPreferences(updatedUserPreferences);
              localStorage.setItem(
                "userPreferences",
                JSON.stringify(updatedUserPreferences),
              );
            }}
          >
            <React.Fragment key=".0">
              <option value="2">2</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="75">75</option>
              <option value="100">100</option>
            </React.Fragment>
          </Select>
        </div>
      </div>
    </div>
  );
}

/**
 * Renders table rows given a list of eCRs. Each row contains an eCR ID linked to its
 * individual eCR viewer page and the stored date.
 * @param listFhirData - The list of eCRs to render.
 * @returns An array of JSX table row elements representing the list of eCRs.
 */
const renderListEcrTableData = (listFhirData: EcrDisplay[]) => {
  return listFhirData.map((item, index) => {
    return (
      <tr key={`table-row-${index}`}>
        <td>
          <a href={`/view-data?id=${item.ecrId}`}>
            {item.patient_first_name} {item.patient_last_name}
          </a>
          <br />
          {"DOB: " + item.patient_date_of_birth || ""}
        </td>
        <td>{item.date_created}</td>
        <td>{item.patient_report_date}</td>
        <td>{item.reportable_condition}</td>
        <td>{item.rule_summary}</td>
      </tr>
    );
  });
};
