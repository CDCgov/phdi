[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluateDemographicsData

# Function: evaluateDemographicsData()

> **evaluateDemographicsData**(`fhirBundle`, `mappings`): [`CompleteData`](../../../utils/interfaces/CompleteData.md)

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing demographic data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

[`CompleteData`](../../../utils/interfaces/CompleteData.md)

An array of evaluated and formatted demographic data.

## Defined in

[src/app/services/evaluateFhirDataService.ts:228](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L228)
