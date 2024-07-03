[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/SideNav](../README.md) / countObjects

# Function: countObjects()

> **countObjects**(`sectionConfigs`): `number`

Counts the total number of `SectionConfig` objects within a given array, including those nested
within `subNavItems` properties.

## Parameters

• **sectionConfigs**: [`SectionConfig`](../classes/SectionConfig.md)[]

An array of `SectionConfig` objects, each potentially containing
  a `subNavItems` property with further `SectionConfig` objects.

## Returns

`number`

The total count of `SectionConfig` objects within the array, including all nested
objects within `subNavItems`.

## Defined in

[src/app/view-data/components/SideNav.tsx:44](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/SideNav.tsx#L44)
