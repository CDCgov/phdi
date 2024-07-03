[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/ecrSummaryService](../README.md) / evaluateEcrSummaryRelevantLabResults

# Function: evaluateEcrSummaryRelevantLabResults()

> **evaluateEcrSummaryRelevantLabResults**(`fhirBundle`, `fhirPathMappings`, `snomedCode`): [`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient data.

• **fhirPathMappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

Object containing fhir path mappings.

• **snomedCode**: `string`

String containing the SNOMED code search parameter.

## Returns

[`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

An array of lab result details objects containing title and value pairs.

## Defined in

[src/app/services/ecrSummaryService.ts:184](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/ecrSummaryService.ts#L184)
