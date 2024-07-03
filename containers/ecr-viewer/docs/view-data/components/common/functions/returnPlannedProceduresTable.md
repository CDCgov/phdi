[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnPlannedProceduresTable

# Function: returnPlannedProceduresTable()

> **returnPlannedProceduresTable**(`carePlanActivities`, `mappings`): `undefined` \| `Element`

## Parameters

• **carePlanActivities**: `CarePlanActivity`[]

An array containing the list of procedures.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

An object containing FHIR path mappings for procedure attributes.

## Returns

`undefined` \| `Element`

- A formatted table React element representing the list of planned procedures, or undefined if the procedures array is empty.

## Defined in

[src/app/view-data/components/common.tsx:459](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/common.tsx#L459)
