from typing import Any

from containers.orchestration.app.DAL.FhirDataModel import FhirDataModel


def entity_to_fhir_model(instance: Any) -> FhirDataModel:
    return FhirDataModel(
        ecr_id=instance["entry"][0]["fullUrl"].split(":")[2], data=instance
    )
