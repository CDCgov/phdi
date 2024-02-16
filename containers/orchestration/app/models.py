import json
from typing import Dict
from typing import Literal
from typing import Optional

from app.constants import PROCESSING_CONFIG_DATA_TYPES
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator


# Request and response models
class OrchestrationRequest(BaseModel):
    """
    The config for requests to the /process endpoint.
    """

    message_type: Literal["ecr", "elr", "vxu", "fhir"] = Field(
        description="The type of message to be validated."
    )
    data_type: Literal["ecr", "zip", "fhir", "hl7"] = Field(
        description=(
            "The type of data of the passed-in message. Must be one of 'ecr', "
            "'fhir', or 'zip'. If `data_type` is set to 'zip', the underlying "
            "unzipped data is assumed to be ecr."
        )
    )
    config_file_name: str = Field(
        description=(
            "The name of a config file in either the `default/` or `custom/`"
            " schemas directory that will define the workflow applied to the"
            " passed data."
        )
    )
    # TODO: Once we land the new orchestrataion overhaul, we should delete this
    # parameter. It's used only in the input specification for the validation
    # service rather than shared across services as a whole, so it's just an
    # unnecessary value we pass around to services that don't need to know
    # about it.
    include_error_types: str = Field(
        description=(
            "A comma separated list of the types of errors that should be"
            + " included in the return response."
            + " Valid types are fatal, errors, warnings, information"
        )
    )

    message: str = Field(description="The message to be validated.")
    rr_data: Optional[str] = Field(
        description="If an eICR message, the accompanying Reportability Response data.",
        default=None,
    )

    @root_validator()
    def validate_rr_with_ecr(cls, values):
        """
        Validates that RR data is supplied if and only if the uploaded data
        is an eCR (or a zip file of an eICR).
        """
        message_type = values.get("message_type")
        data_type = values.get("data_type")
        rr_data = values.get("rr_data")

        if rr_data is not None and (
            message_type != "ecr" or not (data_type == "ecr" or data_type == "zip")
        ):
            raise ValueError(
                "Reportability Response (RR) data is only accepted "
                "for eCR processing requests."
            )
        return values

    @root_validator()
    def validate_types_agree(cls, values):
        """
        Validates that the stream type of a message matches the encoded data
        type of that message. This ensures that data from an eCR stream is
        correctly processed as an eCR and ensures that FHIR data (which is
        held in a different structure) is processed as a dictionary.
        """
        message_type = values.get("message_type")
        data_type = values.get("data_type")
        if message_type == "ecr" and (data_type != "ecr" and data_type != "zip"):
            raise ValueError(
                "For an eCR message, `data_type` must be either `ecr` or `zip`."
            )
        if message_type == "fhir" and data_type != "fhir":
            raise ValueError(
                "`data_type` and `message_type` parameters must both be `fhir` in "
                "order to process a FHIR bundle."
            )
        return values

    @root_validator()
    def validate_fhir_message_is_dict(cls, values):
        """
        Validates that requests specifying a FHIR data type are formatted as
        proper JSON dictionaries for accessing later.
        """
        message = values.get("message")
        data_type = values.get("data_type")
        if data_type == "fhir" and type(json.loads(message)) is not dict:
            raise ValueError(
                "A `data_type` of FHIR requires the input message "
                "to be a valid dictionary."
            )
        return values


class OrchestrationResponse(BaseModel):
    """
    The config for responses from the /extract endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /process endpoint."
    )
    processed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


class ListConfigsResponse(BaseModel):
    """
    The config for responses from the /configs endpoint.
    """

    default_configs: list = Field(
        description="The configs that ship with with this service by default."
    )
    custom_configs: list = Field(
        description="Additional configs that users have uploaded to this service beyond"
        " the ones come by default."
    )


class ProcessingConfigSecondaryFieldModel(BaseModel):
    fhir_path: str
    data_type: PROCESSING_CONFIG_DATA_TYPES
    nullable: bool


class ProcessingConfigFieldModel(BaseModel):
    fhir_path: str
    data_type: PROCESSING_CONFIG_DATA_TYPES
    nullable: bool
    secondary_config: Dict[str, ProcessingConfigSecondaryFieldModel]


class ProcessingConfigModel(BaseModel):
    processing_config: Dict[str, ProcessingConfigFieldModel] = Field(
        description="A JSON formatted processing config to upload."
    )
    overwrite: Optional[bool] = Field(
        description="When `true` if a config already exists for the provided name it "
        "will be replaced. When `false` no action will be taken and the response will "
        "indicate that a config for the given name already exists. To proceed submit a "
        "new request with a different config name or set this field to `true`.",
        default=False,
    )


class PutConfigResponse(BaseModel):
    """
    The config for responses from the /configs endpoint when a config is uploaded.
    """

    message: str = Field(
        'A message describing the result of a request to "/configs/"upload a processing'
        + "config."
    )


class GetConfigResponse(BaseModel):
    """
    The config for responses from the /configs endpoint when a specific config is
    queried.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /process endpoint."
    )
    processing_config: dict = Field(
        description="A configuration for the orchestration app"
    )
