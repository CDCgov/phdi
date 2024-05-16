import { Table } from "@trussworks/react-uswds";
import { ListEcr } from "@/app/api/services/listEcrDataService";

interface ListEcrViewerProps {
  listFhirData: ListEcr;
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
  return (
    <div className="content-wrapper">
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
        <tbody>{renderListEcrTableData(listFhirData)}</tbody>
      </Table>
    </div>
  );
}

/**
 * Renders table rows given a list of eCRs. Each row contains an eCR ID linked to its
 * individual eCR viewer page and the stored date.
 * @param listFhirData - The list of eCRs to render.
 * @returns An array of JSX table row elements representing the list of eCRs.
 */
const renderListEcrTableData = (listFhirData: ListEcr) => {
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
