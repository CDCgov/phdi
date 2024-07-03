[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/ecrSummaryService](../README.md) / evaluateEcrSummaryPatientDetails

# Function: evaluateEcrSummaryPatientDetails()

> **evaluateEcrSummaryPatientDetails**(`fhirBundle`, `fhirPathMappings`): `object`[]

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient data.

• **fhirPathMappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

Object containing fhir path mappings.

## Returns

`object`[]

An array of patient details objects containing title and value pairs.

## Defined in

[src/app/services/ecrSummaryService.ts:49](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/ecrSummaryService.ts#L49)
