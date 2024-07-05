[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnProceduresTable

# Function: returnProceduresTable()

> **returnProceduresTable**(`proceduresArray`, `mappings`): `undefined` \| `Element`

## Parameters

• **proceduresArray**: `Procedure`[]

An array containing the list of procedures.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

An object containing FHIR path mappings for procedure attributes.

## Returns

`undefined` \| `Element`

- A formatted table React element representing the list of procedures, or undefined if the procedures array is empty.

## Defined in

[src/app/view-data/components/common.tsx:419](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/view-data/components/common.tsx#L419)
