[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / evaluateLabOrganizationData

# Function: evaluateLabOrganizationData()

> **evaluateLabOrganizationData**(`id`, `fhirBundle`, `mappings`, `labReportCount`): [`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

## Parameters

• **id**: `string`

id of the organization

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing lab and RR data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

• **labReportCount**: `number`

A number representing the amount of lab reports for a specific organization

## Returns

[`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

The organization display data as an array

## Defined in

[src/app/services/labsService.tsx:553](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/labsService.tsx#L553)
