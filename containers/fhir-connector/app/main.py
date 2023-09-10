from phdi.containers.base_service import BaseService
from pathlib import Path
import requests
import uuid
import json


# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="DIBBS FHIR Connector",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


@app.get(
    "/new-born-screening/{earliest_dob}",
    status_code=200,
)
async def new_born_screening(earliest_dob: str):
    fhir_host = "https://concept01.ehealthexchange.org:52780/fhirproxy/r4/"
    newborn_query = f"{fhir_host}Patient?birthdate=ge{earliest_dob}"
    #fhir_query = f"{fhir_host}Patient?_id=erXuFYUfucBZaryVksYEcMg3"
    username = "svc_skylight"
    password = "TendingTired7Leaves"

    headers = {
        "Accept": "application/json, application/*+json, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/fhir+json; charset=UTF-8",
        "X-DESTINATION": "CernerHelios",
        "X-POU": "TREAT",
        "X-Request-Id": str(uuid.uuid4()),
        "prefer": "return=representation",
        "Cache-Control": "no-cache",
        "OAUTHSCOPES": "system/Condition.read system/Encounter.read system/Immunization.read system/MedicationRequest.read system/Observation.read system/Patient.read system/Procedure.read system/MedicationAdministration.read system/DiagnosticReport.read system/RelatedPerson.read",
    }

    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    session.headers = headers
    newborn_response = session.get(newborn_query)
    newborn_bundle = json.loads(newborn_response.text)
    
    newborn_screening_results = []
    for newborn in newborn_bundle["entry"]:
        screening_loinc_codes = ["73700-7", "73698-3", "54108-6", "54109-4", "58232-0", "57700-7", "73739-5", "73742-9", "2708-6", "8336-0"]
        loinc_fitler = "http://loinc.org|" + ','.join(screening_loinc_codes)
        newborn_id = newborn["resource"]["id"]
        screening_query = f"{fhir_host}Observation?patient={newborn_id}&code={loinc_fitler}"
        screening_response = session.get(screening_query)
        screening_bundle = json.loads(screening_response.text)
        
        if "entry" in screening_bundle:
            screening_bundle["entry"].insert(0,newborn)
            screening_bundle["total"] = len(screening_bundle["entry"])
            
        else:
            screening_bundle = {"resourceType": "Bundle",
                                "id": str(uuid.uuid4()),
                                "type": "searchset",
                                "total": 1,
                                "entry": [newborn]}
        newborn_screening_results.append(screening_bundle)
        
    return newborn_screening_results

