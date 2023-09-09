from phdi.containers.base_service import BaseService
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
import uuid
import urllib



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
    #fhir_query = f"{fhir_host}Patient?birthdate=ge{earliest_dob}"
    fhir_query = f"{fhir_host}Patient?_id=erXuFYUfucBZaryVksYEcMg3"
    username = "svc_skylight"
    password = "TendingTired7Leaves"

    headers = {
        "Accept": "application/json, application/*+json, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/fhir+json; charset=UTF-8",
        "X-DESTINATION": "OpenEpic",
        "X-POU": "TREAT",
        "X-Request-Id": str(uuid.uuid4()),
        "prefer": "return=representation",
        "Cache-Control": "no-cache",
        #"OAUTHSCOPES": "system/Condition.read system/Encounter.read system/Immunization.read system/MedicationRequest.read system/Observation.read system/Patient.read system/Procedure.read system/MedicationAdministration.read system/DiagnosticReport.read system/RelatedPerson.read",
    }

    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    session.headers = headers
    fhir_response = session.get(fhir_query)

    print(fhir_response.status_code)
    print(fhir_response.text)
    breakpoint()
    return
