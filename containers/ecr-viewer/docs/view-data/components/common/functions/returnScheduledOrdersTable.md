[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / returnScheduledOrdersTable

# Function: returnScheduledOrdersTable()

> **returnScheduledOrdersTable**(`fhirBundle`, `mappings`): `undefined` \| `Element`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing care team data.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`undefined` \| `Element`

The JSX element representing the table, or undefined if no scheduled orders are found.

## Defined in

[src/app/view-data/components/common.tsx:354](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/common.tsx#L354)
