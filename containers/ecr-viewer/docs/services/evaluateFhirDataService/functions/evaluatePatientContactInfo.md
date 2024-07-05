[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluatePatientContactInfo

# Function: evaluatePatientContactInfo()

> **evaluatePatientContactInfo**(`fhirBundle`, `mappings`): `string`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient contact info.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`string`

All phone numbers and emails seperated by new lines

## Defined in

[src/app/services/evaluateFhirDataService.ts:97](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L97)
