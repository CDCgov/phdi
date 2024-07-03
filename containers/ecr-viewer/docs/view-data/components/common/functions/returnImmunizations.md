[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnImmunizations

# Function: returnImmunizations()

> **returnImmunizations**(`fhirBundle`, `immunizationsArray`, `mappings`): `undefined` \| `Element`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing patient and immunizations information.

• **immunizationsArray**: `Immunization`[]

An array containing the list of immunizations.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

## Returns

`undefined` \| `Element`

- A formatted table React element representing the list of immunizations, or undefined if the immunizations array is empty.

## Defined in

[src/app/view-data/components/common.tsx:177](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/common.tsx#L177)
