[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/ecrSummaryService](../README.md) / evaluateEcrSummaryRelevantClinicalDetails

# Function: evaluateEcrSummaryRelevantClinicalDetails()

> **evaluateEcrSummaryRelevantClinicalDetails**(`fhirBundle`, `fhirPathMappings`, `snomedCode`): [`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient data.

• **fhirPathMappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

Object containing fhir path mappings.

• **snomedCode**: `string`

String containing the SNOMED code search parameter.

## Returns

[`DisplayDataProps`](../../../DataDisplay/interfaces/DisplayDataProps.md)[]

An array of condition details objects containing title and value pairs.

## Defined in

[src/app/services/ecrSummaryService.ts:141](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/ecrSummaryService.ts#L141)
