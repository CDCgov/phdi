import { noData } from "@/app/utils";
import { Table } from "@trussworks/react-uswds";
import { formatDate } from "@/app/services/formatService";

type AdministeredMedicationProps = {
  medicationData: AdministeredMedicationTableData[];
};
export type AdministeredMedicationTableData = {
  name: string;
  date?: string;
};

/**
 * Returns a table displaying administered medication information.
 * @param props - Props for the component.
 * @param props.medicationData - Array of data of medicine name and start date
 * @returns The JSX element representing the table, or undefined if no administered medications are found.
 */
export const AdministeredMedication = ({
  medicationData,
}: AdministeredMedicationProps) => {
  if (!medicationData?.length) {
    return null;
  }

  const header = ["Medication Name", "Medication Start Date"];
  return (
    <Table
      bordered={false}
      fullWidth={true}
      caption="Administered Medications"
      className={
        "table-caption-margin margin-y-0 border-top border-left border-right"
      }
      data-testid="table"
    >
      <thead>
        <tr>
          {header.map((column) => (
            <th key={`${column}`} scope="col" className="bg-gray-5 minw-15">
              {column}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {medicationData.map((entry, index: number) => {
          return (
            <tr key={`table-row-${index}`}>
              <td>{entry?.name ?? noData}</td>
              <td>{formatDate(entry?.date) ?? noData}</td>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );
};
