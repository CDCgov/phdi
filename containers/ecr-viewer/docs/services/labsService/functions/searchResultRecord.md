[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / searchResultRecord

# Function: searchResultRecord()

> **searchResultRecord**(`result`, `searchKey`): `string`

Recursively searches through a nested array of objects to find values associated with a specified search key.

## Parameters

• **result**: `any`[]

The array of objects to search through.

• **searchKey**: `string`

The key to search for within the objects.

## Returns

`string`

- A comma-separated string containing unique search key values.

## Examples

```ts
result - JSON object that contains the tables for all lab reports
```

```ts
searchKey - Ex. "Analysis Time" or the field that we are searching data for.
```

## Defined in

[src/app/services/labsService.tsx:111](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L111)
