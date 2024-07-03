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

[src/app/services/labsService.tsx:218](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/labsService.tsx#L218)
