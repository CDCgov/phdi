[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluateReference

# Function: evaluateReference()

> **evaluateReference**(`fhirBundle`, `mappings`, `ref`): `any`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing resources.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

Path mappings for resolving references.

• **ref**: `string`

The reference string (e.g., "Patient/123").

## Returns

`any`

The FHIR Resource or undefined if not found.

## Defined in

[src/app/services/evaluateFhirDataService.ts:427](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L427)
