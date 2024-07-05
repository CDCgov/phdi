[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluateSocialData

# Function: evaluateSocialData()

> **evaluateSocialData**(`fhirBundle`, `mappings`): [`CompleteData`](../../../utils/interfaces/CompleteData.md)

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing social data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

[`CompleteData`](../../../utils/interfaces/CompleteData.md)

An array of evaluated and formatted social data.

## Defined in

[src/app/services/evaluateFhirDataService.ts:177](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L177)
