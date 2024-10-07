import { Table } from "@trussworks/react-uswds";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";

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

  const header = [
    { value: "Patient", className: "minw-20" },
    { value: "Received Date", className: "minw-1605" },
    { value: "Encounter Date", className: "minw-1705" },
    { value: "Reportable Condition", className: "minw-2305" },
    { value: "RCKMS Rule Summary", className: "minw-23" },
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
        <tbody>{await renderPage(currentPage)}</tbody>
      </Table>
    </div>
  );
};

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
          <a href={`${basePath}/view-data?id=${item.ecrId}`}>
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

export default EcrTable;
