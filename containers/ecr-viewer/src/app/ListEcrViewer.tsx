"use client";

import { Table } from "@trussworks/react-uswds";
import { Ecr } from "@/app/api/services/listEcrDataService";
import { useState } from "react";
import { Pagination } from "@trussworks/react-uswds";

interface ListEcrViewerProps {
  listFhirData: Ecr[];
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
  const header = ["eCR ID", "Stored Date"];
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
      <div className="homepage-wrapper">
        <Table
          bordered={false}
          fullWidth={true}
          className={"table-homepage-list"}
          data-testid="table"
        >
          <thead>
            <tr>
              {header.map((column) => (
                <th key={`${column}`} scope="col">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>{renderPage(currentPage)}</tbody>
        </Table>
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
const renderListEcrTableData = (listFhirData: Ecr[]) => {
  return listFhirData.map((item, index) => {
    return (
      <tr key={`table-row-${index}`}>
        <td>
          <a href={`/view-data?id=${item.ecrId}`}>{item.ecrId}</a>
        </td>
        <td>{item.dateModified}</td>
      </tr>
    );
  });
};
