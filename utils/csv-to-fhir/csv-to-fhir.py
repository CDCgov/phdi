import csv
import json
import os
import random
import uuid
from datetime import datetime

import pytz
import requests
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.encounter import EncounterParticipant
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.medicationrequest import MedicationRequest
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.specimen import Specimen


def build_patient(row, id, references):
    patient = Patient.construct()
    patient.id = id
    patient.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient|3.1.1"
        ]
    }
    patient.birthDate = row["Date of Birth"]
    patient.gender = row["Administrative Gender"].lower()
    patient.deceasedBoolean = False if row["Deceased Indicator"] == "No" else True

    patient_name = HumanName.construct()
    patient_name.use = "official"
    patient_name.family = row["Patient Last Name"]
    patient_name.given = [
        row["Patient First Name"],
        row["Patient Middle Initial"] if row["Patient Middle Initial"] else None,
    ]
    patient.name = [patient_name]

    patient_address = Address.construct()
    patient_address.use = "home"
    patient_address.line = [row["Patient Street Address"]]
    patient_address.city = row["Patient City"]
    patient_address.state = row["Patient State"]
    patient_address.country = row["Patient Country"]
    patient.address = [patient_address]

    mrn = Identifier.construct()
    mrn.system = "http://hospital.smarthealthit.org"
    mrn.value = str(random.randint(100000, 999999))
    mrn.type = build_codeable_concept(
        "http://terminology.hl7.org/CodeSystem/v2-0203",
        "MR",
        "Medical Record Number",
        "Medical Record Number",
    )
    mrn.use = "usual"
    patient.identifier = [mrn]

    race_extension = Extension(
        url="http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
        extension=[
            Extension(
                url="ombCategory",
                valueCoding=Coding(
                    system="urn:oid:2.16.840.1.113883.6.238",
                    code=row["US Core Code (Race)"],
                    display=row["Race"],
                ),
            ),
            Extension(url="text", valueString=row["Race"]),
        ],
    )

    ethnicity_extension = Extension(
        url="http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
        extension=[
            Extension(
                url="ombCategory",
                valueCoding=Coding(
                    system="urn:oid:2.16.840.1.113883.6.238",
                    code=row["US Core Code (Ethnicity)"].split(" ")[0].strip(),
                    display=row["Ethnicity"],
                ),
            ),
            Extension(url="text", valueString=row["Ethnicity"]),
        ],
    )
    patient.extension = [race_extension, ethnicity_extension]

    reference = Reference.construct()
    reference.reference = f"Patient/{patient.id}"

    return patient, reference


def build_social_history_observation(row, id, references):
    social_history = Observation.construct()
    social_history.status = "final"
    social_history.id = id
    social_history.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-simple-observation|3.1.1"
        ]
    }
    social_history.category = [
        build_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "social-history",
            "Social History",
        )
    ]
    if "smoker" in row["Social History"].lower():
        social_history.meta = {
            "profile": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-smokingstatus|3.1.1"
            ]
        }
        code = "72166-2"
        display = "Tobacco smoking status"
    elif "alcohol" in row["Social History"].lower():
        code = "69721-9"
        display = "Do you ever drink alcohol - including beer or wine [Reported.PHQ]"
    elif "sex" in row["Social History"].lower():
        code = "85736-7"
        display = "Number of sexual partners in last 12 months"
    social_history.effectiveDateTime = datetime.now(pytz.utc)
    social_history.code = build_codeable_concept(
        "http://loinc.org", code, display, display
    )

    social_history.subject = references["Patient"]

    parsed_snomed = row["Social History (SNOMED)"].split("|")
    code = parsed_snomed[0].strip()
    display = parsed_snomed[1].strip()
    social_history.valueCodeableConcept = build_codeable_concept(
        "http://snomed.info/sct", code, display, display
    )

    reference = Reference.construct()
    reference = f"Observation/{social_history.id}"
    return social_history, reference


def build_pregnancy_status_observation(row, id, references):
    social_history = Observation.construct()
    social_history.status = "final"
    social_history.id = id
    social_history.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-pregnancystatus"
        ]
    }
    social_history.category = [
        build_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "social-history",
            "Social History",
        )
    ]
    code = "82810-3"
    display = "Pregnancy status"
    social_history.effectiveDateTime = datetime.now(pytz.utc)
    social_history.code = build_codeable_concept(
        "http://loinc.org", code, display, display
    )

    social_history.subject = references["Patient"]

    parsed_snomed = row["Pregnancy Status (SNOMED)"].split("|")
    code = parsed_snomed[0].strip()
    display = parsed_snomed[1].strip()
    social_history.valueCodeableConcept = build_codeable_concept(
        "http://snomed.info/sct", code, display, display
    )

    reference = Reference.construct()
    reference = f"Observation/{social_history.id}"

    return social_history, reference


def build_organization(row, id, references):
    organization = Organization.construct()
    organization.id = id
    organization.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization|3.1.1"
        ]
    }
    organization.name = row["Facility Name"]
    organization.active = True
    organization_address = Address.construct()
    organization_address.use = "work"
    organization_address.line = [row["Facility Street Address"]]
    organization_address.state = row["Facility State"]
    organization_address.country = row["Facility Country"]
    organization.address = [organization_address]

    reference = Reference.construct()
    reference.reference = f"Organization/{organization.id}"

    return organization, reference


def build_practitioner(row, id, references):
    practitioner = Practitioner.construct()
    practitioner.id = id
    practitioner.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner|3.1.1"
        ]
    }
    identifier = Identifier.construct()
    identifier.system = "http://hl7.org/fhir/sid/us-npi"
    identifier.value = str(random.randint(1000000000, 9999999999))
    practitioner.identifier = [identifier]
    practitioner_name = HumanName.construct()
    practitioner_name.use = "official"
    practitioner_name.family = row["Provider Name"].split(" ")[1].strip()
    practitioner_name.given = [row["Provider Name"].split(" ")[0].strip()]
    practitioner.name = [practitioner_name]

    reference = Reference.construct()
    reference.reference = f"Practitioner/{practitioner.id}"

    return practitioner, reference


def build_encounter(row, id, references):
    encounter = Encounter.construct()
    encounter.status = "finished"
    encounter.id = id
    encounter.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter|3.1.1"
        ]
    }
    encounter.subject = references["Patient"]
    encounter_class = Coding.construct()
    encounter_class.system = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
    encounter_class.code = "AMB"
    encounter_class.display = "ambulatory"
    encounter.class_fhir = encounter_class
    period = Period.construct()
    period.start = row["Encounter EffectiveTime Low"] + TIMEZONE
    period.end = row["Encounter EffectiveTime High"] + TIMEZONE
    encounter.period = period
    encounter.type = [
        build_codeable_concept(
            "http://www.ama-assn.org/go/cpt",
            "99213",
            "Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.",
            "Office Visit",
        )
    ]
    encounter_participant = EncounterParticipant.construct()
    encounter.participant = [encounter_participant]
    encounter.reasonCode = [
        build_codeable_concept(
            "https://hl7.org/fhir/codesystem-encounter-reason-use",
            "HC",
            "Health Concern",
            "Health Concern",
        )
    ]

    if references.get("Organization"):
        encounter.serviceProvider = references["Organization"]
    if references.get("Practitioner"):
        encounter_participant.individual = references["Practitioner"]

    reference = Reference.construct()
    reference.reference = f"Encounter/{encounter.id}"

    return encounter, reference


def build_condition(row, id, references):
    condition = Condition.construct()
    condition.id = id
    condition.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition|3.1.1"
        ]
    }
    condition.subject = references["Patient"]
    condition.category = [
        build_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/condition-category",
            "encounter-diagnosis",
            "Encounter Diagnosis",
        )
    ]
    condition.code = build_codeable_concept(
        "http://hl7.org/fhir/sid/icd-10-cm",
        row["Problem Code (ICD 10)"],
        row["Problem Description (ICD-10)"],
        row["Problem Description (ICD-10)"],
    )
    condition.recordedDate = row["Problem EffectiveTime Low (Onset)"] + TIMEZONE
    condition.verificationStatus = build_codeable_concept(
        "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "confirmed",
        "Confirmed",
    )
    condition.clinicalStatus = build_codeable_concept(
        "http://terminology.hl7.org/CodeSystem/condition-clinical",
        row["Problem Status"].lower(),
        row["Problem Status"],
    )
    if references.get("Encounter"):
        condition.encounter = references["Encounter"]

    reference = Reference.construct()
    reference.reference = f"Condition/{condition.id}"
    return condition, reference


def build_medication_request(row, id, references):
    med_req = MedicationRequest.construct(
        status=row["Medication Status"].lower(), intent="order"
    )
    med_req.medicationCodeableConcept = build_codeable_concept(
        "http://www.nlm.nih.gov/research/umls/rxnorm",
        row["Medication Code"],
        row["Medication Description / Display Name"],
        row["Medication Description / Display Name"],
    )
    med_req.id = id
    med_req.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest|3.1.1"
        ]
    }
    med_req.subject = references["Patient"]
    med_req.authoredOn = row["Medication effectiveTime"] + TIMEZONE
    icd10_reason = build_codeable_concept(
        "http://hl7.org/fhir/sid/icd-10-cm",
        row["Problem Code (ICD 10)"],
        row["Problem Description (ICD-10)"],
        row["Problem Description (ICD-10)"],
    )
    parsed_snomed = row["Problem Code (SNOMED)"].split("|")
    snomed_code = parsed_snomed[0].strip()
    snomed_display = parsed_snomed[1].strip()
    snomed_reason = build_codeable_concept(
        "http://snomed.info/sct", snomed_code, snomed_display, snomed_display
    )
    med_req.reasonCode = [icd10_reason, snomed_reason]
    med_req.dosageInstruction = [
        {"text": " ".join([row["Medication route"], row["Medication Dose / Quantity"]])}
    ]
    if references.get("Encounter"):
        med_req.encounter = references["Encounter"]
    if references.get("Practitioner"):
        med_req.requester = references["Practitioner"]
    if references.get("Condition"):
        med_req.reasonReference = [references["Condition"]]

    reference = Reference.construct()
    reference.reference = f"MedicationRequest/{med_req.id}"
    return med_req, reference


def build_specimen(row, id, references):
    specimen = Specimen.construct()
    specimen.id = id
    specimen.subject = references["Patient"]
    specimen.type = build_codeable_concept(
        "http://terminology.hl7.org/CodeSystem/v2-0487",
        row["Specimen Code"],
        row["Specimen Type"],
    )

    reference = Reference.construct()
    reference.reference = f"Specimen/{specimen.id}"
    return specimen, reference


def build_codeable_concept(system, code, display, text=None):
    codeable_concept = CodeableConcept.construct()
    coding = Coding.construct()
    coding.system = system
    coding.code = code
    coding.display = display
    codeable_concept.coding = [coding]
    if text:
        codeable_concept.text = text
    return codeable_concept


def build_lab_observation(row, id, references):
    observation = Observation.construct()
    observation.status = "final"
    observation.id = id
    observation.meta = {
        "profile": [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab|3.1.1"
        ]
    }
    observation.category = [
        build_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "laboratory",
            "Laboratory",
        )
    ]
    observation.code = build_codeable_concept(
        "http://loinc.org", row["Lab Test code"], row["Lab Test Description"]
    )
    observation.subject = references["Patient"]
    observation.effectiveDateTime = row["Lab Test Date"]
    observation.valueCodeableConcept = build_codeable_concept(
        "http://snomed.info/sct", "260373001", "Detected"
    )
    observation.interpretation = [
        build_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
            "POS",
            row["Abnormal Flag"],
        )
    ]

    if references.get("Encounter"):
        observation.encounter = references["Encounter"]
    if references.get("Specimen"):
        observation.specimen = references["Specimen"]

    reference = Reference.construct()
    reference.reference = f"Observation/{observation.id}"

    return observation, reference


resource_builder_map = {
    "Patient": build_patient,
    "Social History Observation": build_social_history_observation,
    "Practitioner": build_practitioner,
    "Organization": build_organization,
    "Encounter": build_encounter,
    "Condition": build_condition,
    "Medication Request": build_medication_request,
    "Specimen": build_specimen,
    "Lab Observation": build_lab_observation,
    "Pregnancy Status Observation": build_pregnancy_status_observation,
}

TIMEZONE = "-04:00"
FHIR_SERVER = "https://gw.interop.community/CDCOPHDSTHELIOS/open"
with open("Synthetic Data_FHIR_KS_NU_0806_v3 (Updated).csv", mode="r") as file:
    all_rows = list(csv.reader(file))

# Drop header rows
data = all_rows[5:]
header = all_rows[4]
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

for index, row in enumerate(data):
    row_dict = dict(zip(header, row))
    bundle = Bundle.construct()
    bundle.type = "batch"
    bundle.id = str(uuid.uuid4())
    bundle.entry = []
    references = {}
    for resource_name, builder in resource_builder_map.items():
        if row_dict.get(resource_name) is None:
            row_dict[resource_name] = str(uuid.uuid4())
            if index == 0:
                header.append(resource_name)
        id = row_dict[resource_name]
        resource, reference = builder(row_dict, id, references)
        references[resource_name] = reference
        bundle.entry.append(
            {
                "fullUrl": f"urn:uuid:{resource.id}",
                "resource": resource,
                "request": {
                    "method": "PUT",
                    "url": f"{resource.resource_type}/{resource.id}",
                },
            }
        )

    with open(
        f"output/{row_dict['Patient Last Name']}_{row_dict['Patient First Name']}_{references['Patient'].reference.split('/')[1]}.json",
        "w",
    ) as f:
        f.write(bundle.json(indent=4))
    all_rows[index + 5] = list(row_dict.values())

    response = requests.post(
        FHIR_SERVER,
        json=json.loads(bundle.json()),
        headers={"Content-Type": "application/fhir+json"},
    )

    if response.status_code not in [200, 201]:
        print(
            f"Failed to upload {row_dict['Patient First Name']} {row_dict['Patient Last Name']}"
        )
        continue
    for entry in response.json().get("entry", []):
        status = entry.get("response", {}).get("status")
        if "201" not in status and "200" not in status:
            print(
                f"Failed to upload {row_dict['Patient First Name']} {row_dict['Patient Last Name']}"
            )
            continue
    print(f"Uploaded {row_dict['Patient First Name']} {row_dict['Patient Last Name']}")


all_rows[4] = header
with open("Synthetic Data_FHIR_KS_NU_0806_v3 (Updated).csv", mode="w") as file:
    writer = csv.writer(file)
    writer.writerows(all_rows)
