[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/formatService](../README.md) / formatTablesToJSON

# Function: formatTablesToJSON()

> **formatTablesToJSON**(`htmlString`): [`TableJson`](../interfaces/TableJson.md)[]

Parses an HTML string containing tables or a list of tables and converts each table into a JSON array of objects.
Each <li> item represents a different lab result. The resulting JSON objects contain the data-id (Result ID)
and text content of the <li> items, along with an array of JSON representations of the tables contained within each <li> item.

## Parameters

• **htmlString**: `string`

The HTML string containing tables to be parsed.

## Returns

[`TableJson`](../interfaces/TableJson.md)[]

- An array of JSON objects representing the list items and their tables from the HTML string.

[{resultId: 'Result.123', resultName: 'foo', tables: [{}, {},...]}, ...]

## Example

```ts

```

## Defined in

[src/app/services/formatService.tsx:327](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/formatService.tsx#L327)
