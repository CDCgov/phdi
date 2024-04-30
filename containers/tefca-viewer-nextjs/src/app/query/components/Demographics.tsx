import { Patient, HumanName, Address, ContactPoint, Identifier } from 'fhir/r4';
import { DisplayData } from '@/app/utils';
import { DataDisplay } from '@/app/utils';
import * as dateFns from "date-fns";
import {evaluate} from "fhirpath";

export interface DemographicsProps {
    patient: Patient;
}

function formatDemographics(patient: Patient) {

    const demographicData: DisplayData[] = [
        {
          title: "Patient Name",
          value: formatName(patient.name ?? []),
        },
        { 
          title: "DOB",
          value: patient.birthDate ?? "",
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
          value: evaluate(patient, "Patient.extension.where(url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity').extension.first().valueCoding.display")[0],
        },
        {
          title: "Ethnicity",
          value: evaluate(patient, "Patient.extension.where(url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race').extension.first().valueCoding.display")[0],
        },
        {
          title: "Tribal Affiliation",
          value: evaluate(patient, "Patient.extension.where(url='http: //hl7.org/fhir/us/ecr/StructureDefinition/us-ph-tribal-affiliation-extension').extension.where(url='TribeName').value.display")[0],
        },
        {
          title: "Preferred Language",
          value: evaluate(patient, "Patient.communication.first().language.coding.first().display")[0],
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

function formatName(names: HumanName[]) {
    let name = "";
    if (names.length > 0) {
        name = names[0].given?.join(" ") + " " + names[0].family;
    }
    return name;
}

function formatAddress(address: Address[]) {
    let formattedAddress = "";
    if (address.length > 0) {
        formattedAddress = address[0]?.line?.join("\n") + "\n" + address[0].city + ", " + address[0].state + " " + address[0].postalCode;
    }
    return formattedAddress;
}

function formatContact(contacts: ContactPoint[]) {
    return (
        contacts.map((contact) => {
            if (contact.system === "phone") {
                return `${contact.use}: ${contact.value}`;
            }
            else if (contact.system === "email") {
                return contact.value;
            }
        }
        ).join("\n")
    )
}

function formatIdentifier(identifier: Identifier[]) {
    return (
        identifier.map((id) => {
            let idType = id.type?.coding?.[0].display ?? "";
            if (idType === "") {
                idType = id.type?.text ?? "";
            }

            return `${idType}: ${id.value}`;
        }
        ).join("\n")
    )
}

export const calculatePatientAge = (patient: Patient) => {

    if (patient.birthDate) {
      const patientDOB = new Date(patient.birthDate);
      const today = new Date();
      return dateFns.differenceInYears(today, patientDOB);
    }
  };

export default function Demographics(props: DemographicsProps) {

    const demographicData = formatDemographics(props.patient);

    return (
        <div>
            {demographicData.map((item, index) => (
                <DataDisplay item={item} key={index} />
            ))}
        </div>
    );

}