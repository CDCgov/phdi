[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnCareTeamTable

# Function: returnCareTeamTable()

> **returnCareTeamTable**(`bundle`, `mappings`): `undefined` \| `Element`

## Parameters

• **bundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing care team data.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`undefined` \| `Element`

The JSX element representing the care team table, or undefined if no care team participants are found.

## Defined in

[src/app/view-data/components/common.tsx:98](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/view-data/components/common.tsx#L98)
