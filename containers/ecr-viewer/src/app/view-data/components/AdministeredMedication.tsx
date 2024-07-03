import { noData, PathMappings } from "@/app/utils";
import { Bundle, Medication, MedicationAdministration } from "fhir/r4";
import { evaluateReference } from "@/app/services/evaluateFhirDataService";
import { Table } from "@trussworks/react-uswds";
import { formatDate } from "@/app/services/formatService";

type AdministeredMedicationProps = {
  fhirBundle: Bundle;
  mappings: PathMappings;
  administeredMedicationReferences?: string[];
};
/**
 * Returns a table displaying administered medication information.
 * @param props - Props for the component.
 * @param props.fhirBundle - The FHIR bundle containing care team data.
 * @param props.mappings - The object containing the fhir paths.
 * @param props.administeredMedicationReferences - The object containing administered medication references
 * @returns The JSX element representing the table, or undefined if no administered medications are found.
 */
export const AdministeredMedication = ({
  fhirBundle,
  mappings,
  administeredMedicationReferences,
}: AdministeredMedicationProps) => {
  if (!administeredMedicationReferences?.length) {
    return null;
  }
  const administeredMedications: MedicationAdministration[] =
    administeredMedicationReferences.map((ref) =>
      evaluateReference(fhirBundle, mappings, ref),
    );

  const tableValues = administeredMedications.map((administeredMedication) => {
    if (administeredMedication?.medicationReference?.reference) {
      const medication: Medication = evaluateReference(
        fhirBundle,
        mappings,
        administeredMedication.medicationReference.reference,
      );
      return {
        date:
          administeredMedication.effectiveDateTime ??
          administeredMedication.effectivePeriod?.start,
        medicine: medication?.code?.coding?.[0]?.display,
      };
    }
  });

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
        {tableValues.map((entry, index: number) => {
          return (
            <tr key={`table-row-${index}`}>
              <td>{entry?.medicine ?? noData}</td>
              <td>{formatDate(entry?.date) ?? noData}</td>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );
};
