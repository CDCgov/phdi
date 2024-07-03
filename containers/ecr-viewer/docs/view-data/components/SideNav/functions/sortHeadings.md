[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/SideNav](../README.md) / sortHeadings

# Function: sortHeadings()

> **sortHeadings**(`headings`): [`SectionConfig`](../classes/SectionConfig.md)[]

## Parameters

• **headings**: `HeadingObject`[]

An array of heading objects to be sorted. Each `HeadingObject`
  must have a `text` property for the section title and a
  `priority` property that determines the heading's hierarchical level.

## Returns

[`SectionConfig`](../classes/SectionConfig.md)[]

An array of `SectionConfig` objects representing the structured hierarchy
  of headings. Each `SectionConfig` may contain nested `SectionConfig` objects
  if the original headings array indicated a nested structure based on priorities.

## Defined in

[src/app/view-data/components/SideNav.tsx:88](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/SideNav.tsx#L88)
