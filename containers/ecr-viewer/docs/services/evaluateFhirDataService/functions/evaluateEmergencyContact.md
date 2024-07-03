[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / evaluateEmergencyContact

# Function: evaluateEmergencyContact()

> **evaluateEmergencyContact**(`fhirBundle`, `mappings`): `undefined` \| `string`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient information.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`undefined` \| `string`

The formatted emergency contact information.

## Defined in

[src/app/services/evaluateFhirDataService.ts:376](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L376)
