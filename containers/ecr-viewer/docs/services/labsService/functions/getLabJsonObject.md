[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / getLabJsonObject

# Function: getLabJsonObject()

> **getLabJsonObject**(`report`, `fhirBundle`, `mappings`): [`TableJson`](../../formatService/interfaces/TableJson.md)

## Parameters

• **report**: [`LabReport`](../interfaces/LabReport.md)

The LabReport object containing information about the lab report.

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR Bundle object containing relevant FHIR resources.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The PathMappings object containing mappings for extracting data.

## Returns

[`TableJson`](../../formatService/interfaces/TableJson.md)

The JSON representation of the lab report.

## Defined in

[src/app/services/labsService.tsx:66](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/labsService.tsx#L66)
