[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / returnFieldValueFromLabHtmlString

# Function: returnFieldValueFromLabHtmlString()

> **returnFieldValueFromLabHtmlString**(`labReportJson`, `fieldName`): `ReactNode`

## Parameters

• **labReportJson**: [`TableJson`](../../formatService/interfaces/TableJson.md)

A JSON object representing the lab report HTML string

• **fieldName**: `string`

A string containing the field name for which the value is being searched.

## Returns

`ReactNode`

A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.

## Defined in

[src/app/services/labsService.tsx:218](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L218)
