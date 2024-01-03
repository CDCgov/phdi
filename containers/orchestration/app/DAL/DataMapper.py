from typing import Any

from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel


def entity_to_fhir_model(instance: Any) -> PostgresFhirDataModel:
    return PostgresFhirDataModel(
        ecr_id=instance["entry"][0]["fullUrl"].split(":")[2], data=instance
    )
