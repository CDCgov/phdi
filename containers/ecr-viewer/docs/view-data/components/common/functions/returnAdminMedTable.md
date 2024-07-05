[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnAdminMedTable

# Function: returnAdminMedTable()

> **returnAdminMedTable**(`fhirBundle`, `mappings`): `undefined` \| `Element`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing care team data.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`undefined` \| `Element`

The JSX element representing the table, or undefined if no administed medications are found.

## Defined in

[src/app/view-data/components/common.tsx:42](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/view-data/components/common.tsx#L42)
