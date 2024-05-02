from typing import Dict
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator

PARSING_SCHEMA_DATA_TYPES = Literal[
    "string", "integer", "float", "boolean", "date", "datetime", "array", "struct"
]
PHDC_REPORT_TYPES = Literal[
    "case_report", "contact_record", "lab_report", "morbidity_report"
]


def validate_secondary_reference_fields(values):
    """
    Function that determines whether the schema
      given to message_parser is correctly formatted

    :param values: parsing_schema to determine how to transform data
      with message_parser

    :raises ValueError: raises for two reasons:
      1. If a secondary field in the parsing schema references another resource,
      parsing schema must include a reference_lookup
      2. If a secondary field in the parsing schema includes a reference_lookup,
      that reference_lookup must start with Bundle

    :return values: if parsing_schema correctly formated, return parsing_schema
    """
    schema = values.get("parsing_schema", {})
    for field in schema:
        for _, secondary_field_definition in (
            schema[field].get("secondary_schema", {}).items()
        ):
            if (
                secondary_field_definition.get("fhir_path", "").startswith("Bundle")
                and "reference_lookup" not in secondary_field_definition
            ):
                raise ValueError(
                    "Secondary fields in the parsing schema that reference other "
                    "resources must include a `reference_lookup` field that "
                    "identifies where the reference ID can be found."
                )
            if (
                "reference_lookup" in secondary_field_definition
                and not secondary_field_definition.get("fhir_path").startswith("Bundle")
            ):
                raise ValueError(
                    "Secondary fields in the parsing schema that provide "
                    "`reference_lookup` locations must have a `fhir_path` that "
                    "begins with `Bundle` and identifies the type of resource "
                    "being referenced."
                )
    return values


class ParseMessageInput(BaseModel):
    """
    The schema for requests to the /extract endpoint.
    """

    message_format: Literal["fhir", "hl7v2", "ecr"] = Field(
        description="The format of the message."
    )
    message_type: Optional[Literal["ecr", "elr", "vxu"]] = Field(
        description="The type of message that values will be extracted from. Required "
        "when 'message_format is not FHIR."
    )
    parsing_schema: Optional[dict] = Field(
        description="A schema describing which fields to extract from the message. This"
        " must be a JSON object with key:value pairs of the form "
        "<my-field>:<FHIR-to-my-field>.",
        default={},
    )
    parsing_schema_name: Optional[str] = Field(
        description="The name of a schema that was previously"
        " loaded in the service to use to extract fields from the message.",
        default="",
    )
    fhir_converter_url: Optional[str] = Field(
        description="The URL of an instance of the PHDI FHIR converter. Required when "
        "the message is not already in FHIR format.",
        default="",
    )
    credential_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="The type of credential manager to use for authentication with a "
        "FHIR converter when conversion to FHIR is required.",
        default=None,
    )
    include_metadata: Optional[Literal["true", "false"]] = Field(
        description="Boolean to include metadata in the response.",
        default=None,
    )
    message: Union[str, dict] = Field(description="The message to be parsed.")

    @root_validator
    def require_message_type_when_not_fhir(cls, values):
        """
        Function that checks when non-fhir-formatted data is given whether a
          message_type has been included with API call

        :param cls: the ParseMessageInput class
        :param values: the message_format provided by the user
        :raises ValueError: errors when message_type is None
          when message_format is not "fhir"
        :return values: the message_format provided by the user
        """
        if (
            values.get("message_format") != "fhir"
            and values.get("message_type") is None
        ):
            raise ValueError(
                "When the message format is not FHIR then the message type must be "
                "included."
            )
        return values

    @root_validator
    def prohibit_schema_and_schema_name(cls, values):
        """
        Function that checks whether the user has provided
          both parsing_schema and parsing_schema_name;
          only one should be provided for message_parser to work correctly.

        :param cls: the ParseMessageInput class
        :param values: the parsing_schema and parsing_schema_name provided by the user
        :raises ValueError: error when both parsing_schema and
          parsing_schema_name are provided in API call.
        :return values: the parsing_schema and parsing_schema_name provided by the user
        """
        if (
            values.get("parsing_schema") != {}
            and values.get("parsing_schema_name") != ""
        ):
            raise ValueError(
                "Values for both 'parsing_schema' and 'parsing_schema_name' have been "
                "provided. Only one of these values is permited."
            )
        return values

    @root_validator
    def require_schema_or_schema_name(cls, values):
        """
        Function that checks whether the user has provided
          one of either parsing_schema and parsing_schema_name;
          one (and only one!) should be provided for message_parser to work correctly.

        :param cls: the ParseMessageInput class
        :param values: the parsing_schema and parsing_schema_name provided by the user
        :raises ValueError: error when both pasing_schema and parsing_schema_name
          are missing from API call.
        :return values: the parsing_schema and parsing_schema_name provided by the user
        """
        if (
            values.get("parsing_schema") == {}
            and values.get("parsing_schema_name") == ""
        ):
            raise ValueError(
                "Values for 'parsing_schema' and 'parsing_schema_name' have not been "
                "provided. One, but not both, of these values is required."
            )
        return values

    # TODO: As part of future work, move validation of the schema more fully
    # into pydanatic, rather than duplicate schema validation on each model
    # and the schema upload
    @root_validator
    def require_reference_fields_to_have_lookups(cls, values):
        """
        Ensures that reference fields in a model have corresponding lookups.

        :param cls: The class on which this validator is defined.
        :param values: The dictionary of field values to validate.
        :return: The validated (and potentially modified) dictionary of field
            values.
        """
        return validate_secondary_reference_fields(values)


class ParseMessageResponse(BaseModel):
    """
    The schema for responses from the /extract endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    parsed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


class FhirToPhdcInput(BaseModel):
    """
    The schema for requests to the /fhir-to-phdc endpoint.
    """

    phdc_report_type: PHDC_REPORT_TYPES = Field(
        description="The type of PHDC document the user wants returned to them."
        " The choice of report type should reflect the type of the incoming data"
        " and determines which PHDC schema is used when extracting."
    )
    message: dict = Field(description="The FHIR bundle to extract from.")


class FhirToPhdcResponse(BaseModel):
    """
    The schema for responses from the /fhir-to-phdc endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    parsed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


class ListSchemasResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint.
    """

    default_schemas: list = Field(
        description="The schemas that ship with with this service by default."
    )
    custom_schemas: list = Field(
        description="Additional schemas that users have uploaded to this service beyond"
        " the ones come by default."
    )


class GetSchemaResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint when a specific schema is
    queried.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    parsing_schema: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


class ParsingSchemaTertiaryFieldModel(BaseModel):
    fhir_path: str
    data_type: PARSING_SCHEMA_DATA_TYPES
    nullable: bool


class ParsingSchemaSecondaryFieldModel(BaseModel):
    fhir_path: str
    data_type: PARSING_SCHEMA_DATA_TYPES
    nullable: bool
    secondary_schema: Optional[Dict[str, ParsingSchemaTertiaryFieldModel]]


class ParsingSchemaFieldModel(BaseModel):
    fhir_path: str
    data_type: PARSING_SCHEMA_DATA_TYPES
    nullable: bool
    secondary_schema: Optional[Dict[str, ParsingSchemaSecondaryFieldModel]]


class ParsingSchemaModel(BaseModel):
    parsing_schema: Dict[str, ParsingSchemaFieldModel] = Field(
        description="A JSON formatted parsing schema to upload."
    )
    overwrite: Optional[bool] = Field(
        description="When `true` if a schema already exists for the provided name it "
        "will be replaced. When `false` no action will be taken and the response will "
        "indicate that a schema for the given name already exists. To proceed submit a "
        "new request with a different schema name or set this field to `true`.",
        default=False,
    )


class PutSchemaResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint when a schema is uploaded.
    """

    message: str = Field(
        "A message describing the result of a request to " "upload a parsing schema."
    )
