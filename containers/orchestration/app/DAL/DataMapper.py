from typing import Any

from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel


def entity_to_fhir_model(instance: Any) -> PostgresFhirDataModel:
    """
    Converts a generic entity instance to a `PostgresFhirDataModel`.

    Parameters:
        instance (Any): The entity instance to convert, expected to have
                        a specific structure with an 'entry' list.

    Returns:
        PostgresFhirDataModel: The initialized FHIR data model.
    """
    return PostgresFhirDataModel(
        ecr_id=instance["entry"][0]["fullUrl"].split(":")[2], data=instance
    )
