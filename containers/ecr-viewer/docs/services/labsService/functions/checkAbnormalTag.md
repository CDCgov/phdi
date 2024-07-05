[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / checkAbnormalTag

# Function: checkAbnormalTag()

> **checkAbnormalTag**(`labReportJson`): `boolean`

## Parameters

• **labReportJson**: [`TableJson`](../../formatService/interfaces/TableJson.md)

A JSON object representing the lab report HTML string

## Returns

`boolean`

True if the result name includes "abnormal" (case insensitive), otherwise false. Will also return false if lab does not have JSON object.

## Defined in

[src/app/services/labsService.tsx:94](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L94)
