import { Patient } from "fhir/r4";
import { DisplayData } from "@/app/utils";
import { DataDisplay } from "@/app/utils";
import * as dateFns from "date-fns";
import { evaluate } from "fhirpath";

import {
  formatName,
  formatAddress,
  formatContact,
  formatIdentifier,
  formatDate,
} from "../../format-service";

/**
 * Displays the demographic information of a patient.
 * @param {Patient} patient - The patient to display demographic information for.
 * @returns {React.FC} The Demographics component.
 */
export interface DemographicsProps {
  patient: Patient;
}

/**
 * Displays the demographic information of a patient.
 * @param props - The props for the Demographics component.
 * @param props.patient - The patient resource to display demographic information for.
 * @returns The Demographics component.
 */
const Demographics: React.FC<DemographicsProps> = ({ patient }) => {
  const demographicData = formatDemographics(patient);

  return (
    <div>
      {demographicData.map((item, index) => (
        <DataDisplay item={item} key={index} />
      ))}
    </div>
  );
};

export default Demographics;

/**
 * Formats the demographic information of a patient.
 * @param patient - The patient to format demographic information for.
 * @returns The formatted demographic information as an array of DisplayData objects.
 */
function formatDemographics(patient: Patient): DisplayData[] {
  const demographicData: DisplayData[] = [
    {
      title: "Patient Name",
      value: formatName(patient.name ?? []),
    },
    {
      title: "DOB",
      value: formatDate(patient.birthDate),
    },
    {
      title: "Current Age",
      value: calculatePatientAge(patient)?.toString(),
    },
    {
      title: "Sex",
      value: patient.gender ?? "",
    },
    {
      title: "Race",
      value: evaluate(
        patient,
        "Patient.extension.where(url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity').extension.first().valueCoding.display",
      )[0],
    },
    {
      title: "Ethnicity",
      value: evaluate(
        patient,
        "Patient.extension.where(url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race').extension.first().valueCoding.display",
      )[0],
    },
    {
      title: "Tribal Affiliation",
      value: evaluate(
        patient,
        "Patient.extension.where(url='http: //hl7.org/fhir/us/ecr/StructureDefinition/us-ph-tribal-affiliation-extension').extension.where(url='TribeName').value.display",
      )[0],
    },
    {
      title: "Preferred Language",
      value: evaluate(
        patient,
        "Patient.communication.first().language.coding.first().display",
      )[0],
    },
    {
      title: "Address",
      value: formatAddress(patient.address ?? []),
    },
    {
      title: "Contact",
      value: formatContact(patient.telecom ?? []),
    },
    {
      title: "Patient Identifiers",
      value: formatIdentifier(patient.identifier ?? []),
    },
  ];

  return demographicData;
}

/**
 * Calculates the age of a patient based on their birth date.
 * @param patient - The patient to calculate the age for.
 * @returns The age of the patient.
 */
export function calculatePatientAge(patient: Patient): number | undefined {
  if (patient.birthDate) {
    const patientDOB = new Date(patient.birthDate);
    const today = new Date();
    return dateFns.differenceInYears(today, patientDOB);
  }
}
