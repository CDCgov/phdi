import { noData } from "@/app/utils";
import { formatDate } from "@/app/services/formatService";
import {
  BuildHeaders,
  BuildTable,
} from "@/app/view-data/components/EvaluateTable";

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

  const headers = BuildHeaders([
    { columnName: "Medication Name", className: "bg-gray-5 minw-15" },
    { columnName: "Medication Start Date", className: "bg-gray-5 minw-15" },
  ]);
  const tableRows = medicationData.map((entry, index: number) => {
    return (
      <tr key={`table-row-${index}`}>
        <td>{entry?.name ?? noData}</td>
        <td>{formatDate(entry?.date) ?? noData}</td>
      </tr>
    );
  });

  return (
    <BuildTable
      headers={headers}
      tableRows={tableRows}
      caption="Administered Medications"
      className={"margin-y-0"}
      fixed={false}
    />
  );
};
