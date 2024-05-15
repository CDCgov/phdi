import { Table } from "@trussworks/react-uswds";
import { ListEcr } from "@/app/services/processService";

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
        <tbody>
          {listFhirData.map((item, index) => {
            return (
              <tr key={`table-row-${index}`}>
                <td>
                  <a href={`/view-data?id=${item.ecr_id}`}>{item.ecr_id}</a>
                </td>
                <td>{item.dateModified}</td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </div>
  );
}
