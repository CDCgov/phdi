from phdi.containers.base_service import BaseService
from pathlib import Path
import requests
import uuid
import json
from pydantic import BaseModel
from typing import Optional, Literal

USE_CASES = Literal["social-determinants", "new-born-screening"]

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="DIBBS FHIR Connector",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


class UseCaseQueryRequest(BaseModel):
    first_name: str
    last_name: str
    dob: str
    mrn: Optional[str]
    phone: Optional[str]
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]


@app.post("/use-case-query/{use_case}")
async def use_case_query(use_case: USE_CASES, input: UseCaseQueryRequest):
    fhir_host = "https://gw.interop.community/HeliosConnectathonSa/open"

    # Find Patient

    patient_query = f"{fhir_host}/Patient?given={input.first_name}&family={input.last_name}&birthdate={input.dob}"
    response = requests.get(patient_query)

    if response.status_code != 200:
        return {
            "error": "Patient search failed.",
            "status_code": response.status_code,
            "query": patient_query,
            "fhir_server_response": response.text,
        }

    patient_searchset = response.json()

    if patient_searchset["total"] > 1:
        return {"error": "Multiple patients found. Please refine your search."}
    elif patient_searchset["total"] == 0:
        return {"error": "No patients found. Please refine your search."}

    patient_id = patient_searchset["entry"][0]["resource"]["id"]

    print(patient_id)
    # Use Case Query

    if use_case == "social-determinants":
        use_case_query = (
            f"{fhir_host}/Observation?subject=Patient/{patient_id}&category=survey"
        )

    elif use_case == "new-born-screening":
        use_case_query = (
            f"{fhir_host}/Observation?subject=Patient/{patient_id}&category=laboratory"
        )
        screening_loinc_codes = [
            "73700-7",
            "73698-3",
            "54108-6",
            "54109-4",
            "58232-0",
            "57700-7",
            "73739-5",
            "73742-9",
            "2708-6",
            "8336-0",
        ]
        loinc_fitler = "http://loinc.org|" + ",".join(screening_loinc_codes)
        use_case_query = f"{use_case_query}&code={loinc_fitler}"

    print(use_case_query)

    use_case_response = requests.get(use_case_query)

    return use_case_response.json()


@app.get(
    "/new-born-screening/{earliest_dob}",
    status_code=200,
)
async def new_born_screening(earliest_dob: str):
    fhir_host = "https://concept01.ehealthexchange.org:52780/fhirproxy/r4/"
    newborn_query = f"{fhir_host}Patient?birthdate=ge{earliest_dob}"
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
    print(newborn_response.text)
    print(newborn_response.status_code)
    # newborn_bundle = json.loads(newborn_response.text)

    # newborn_screening_results = []
    # for newborn in newborn_bundle["entry"]:
    #     screening_loinc_codes = ["73700-7", "73698-3", "54108-6", "54109-4", "58232-0", "57700-7", "73739-5", "73742-9", "2708-6", "8336-0"]
    #     loinc_fitler = "http://loinc.org|" + ','.join(screening_loinc_codes)
    #     newborn_id = newborn["resource"]["id"]
    #     screening_query = f"{fhir_host}Observation?patient={newborn_id}&code={loinc_fitler}"
    #     screening_response = session.get(screening_query)
    #     screening_bundle = json.loads(screening_response.text)

    #     if "entry" in screening_bundle:
    #         screening_bundle["entry"].insert(0,newborn)
    #         screening_bundle["total"] = len(screening_bundle["entry"])

    #     else:
    #         screening_bundle = {"resourceType": "Bundle",
    #                             "id": str(uuid.uuid4()),
    #                             "type": "searchset",
    #                             "total": 1,
    #                             "entry": [newborn]}
    #     newborn_screening_results.append(screening_bundle)

    return {
        "query": newborn_query,
        "headers": headers,
        "username": username,
        "password": password,
        "response_text": newborn_response.text,
        "response_status_code": newborn_response.status_code,
    }


# async def make_fhir_request(url :str, session: aiohttp.ClientSession):
#     response = await session.get(url=url)
#     fhir_bundle = await json.loads(response.text)
#     return fhir_bundle

# async def main(urls):
#     async with aiohttp.ClientSession() as session:
#    	 tasks = []
#    	 for url in urls:
#    		 tasks.append(get_url_data(url=url, session=session))
#    	 results = await asyncio.gather(*tasks, return_exceptions=True)
#     return results
