from pydantic import BaseModel, Field, root_validator
from typing import Literal, Optional, Dict
from fastapi import UploadFile
from app.constants import PROCESSING_CONFIG_DATA_TYPES


# Request and response models
class ProcessMessageRequest(BaseModel):
    """
    The config for requests to the /process endpoint.
    """

    message_type: Optional[Literal["ecr", "elr", "vxu", "fhir"]] = Field(
        description="The type of message to be validated."
    )
    include_error_types: Optional[str] = Field(
        description=(
            "A comma separated list of the types of errors that should be"
            + " included in the return response."
            + " Valid types are fatal, errors, warnings, information"
        )
    )

    upload_file: Optional[UploadFile] = Field(description="The ZIP file with ECR")

    message: Optional[str] = Field(description="The message to be validated.")

    @root_validator(pre=True, allow_reuse=True)
    def validate_fields(cls, values):
        upload_file = values.get("upload_file")
        message = values.get("message")

        if upload_file is None and message is None:
            raise ValueError(
                "At least one of 'upload_file' or 'message' must be provided"
            )

        if upload_file is not None and message is not None:
            raise ValueError(
                "Only one of 'upload_file' or 'message' should be provided"
            )

        return values


class ProcessMessageResponse(BaseModel):
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
