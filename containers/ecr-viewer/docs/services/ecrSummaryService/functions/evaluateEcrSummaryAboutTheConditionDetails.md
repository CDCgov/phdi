[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/ecrSummaryService](../README.md) / evaluateEcrSummaryAboutTheConditionDetails

# Function: evaluateEcrSummaryAboutTheConditionDetails()

> **evaluateEcrSummaryAboutTheConditionDetails**(`fhirBundle`, `fhirPathMappings`): `object`[]

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient data.

• **fhirPathMappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

Object containing fhir path mappings.

## Returns

`object`[]

An array of condition details objects containing title and value pairs.

## Defined in

[src/app/services/ecrSummaryService.ts:114](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/ecrSummaryService.ts#L114)
