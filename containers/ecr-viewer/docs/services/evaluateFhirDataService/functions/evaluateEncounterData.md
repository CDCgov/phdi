[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluateEncounterData

# Function: evaluateEncounterData()

> **evaluateEncounterData**(`fhirBundle`, `mappings`): [`CompleteData`](../../../utils/interfaces/CompleteData.md)

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing encounter data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

[`CompleteData`](../../../utils/interfaces/CompleteData.md)

An array of evaluated and formatted encounter data.

## Defined in

[src/app/services/evaluateFhirDataService.ts:294](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L294)
