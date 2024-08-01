"use client";

import { Table } from "@trussworks/react-uswds";
import { useState } from "react";
import { Pagination } from "@trussworks/react-uswds";
import { EcrDisplay } from "@/app/api/services/listEcrDataService";

interface ListEcrViewerProps {
  listFhirData: EcrDisplay[];
}

/**
 * Renders a list of eCR data with viewer.
 * @param listFhirData - The list of eCRs to render.
 * @param listFhirData.listFhirData The array of eCRs IDs and date values.
 * @returns The JSX element (table) representing the rendered list of eCRs.
 */
export default function ListECRViewer({
  listFhirData,
}: ListEcrViewerProps): JSX.Element {
  const header = [
    { value: "Patient", className: "minw-160" },
    { value: "Received Date", className: "minw-132" },
    { value: "Encounter Date", className: "minw-140" },
    { value: "Reportable Condition", className: "minw-188" },
    { value: "RCKMS Rule Summary", className: "minw-184" },
  ];
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 25;
  const totalPages = Math.ceil(listFhirData.length / itemsPerPage);

  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
    renderPage(pageNumber);
  };

  const renderPage = (pageNumber: number) => {
    const startIndex = (pageNumber - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = listFhirData.slice(startIndex, endIndex);
    return renderListEcrTableData(pageData);
  };

  return (
    <div className="main-container">
      <div className="ecr-library-wrapper">
        <Table
          bordered={false}
          fullWidth={true}
          striped={true}
          fixed={true}
          className={"table-ecr-library"}
          data-testid="table"
        >
          <thead>
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
      <div className="pagination-bar">
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
        />
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
