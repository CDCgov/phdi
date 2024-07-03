[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/evaluateFhirDataService](../README.md) / calculatePatientAge

# Function: calculatePatientAge()

> **calculatePatientAge**(`fhirBundle`, `fhirPathMappings`, `givenDate`?): `undefined` \| `number`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient information.

• **fhirPathMappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The mappings for retrieving patient date of birth.

• **givenDate?**: `string`

Optional. The target date to calculate the age. Defaults to the current date if not provided.

## Returns

`undefined` \| `number`

- The age of the patient in years, or undefined if date of birth is not available.

## Defined in

[src/app/services/evaluateFhirDataService.ts:158](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/evaluateFhirDataService.ts#L158)
