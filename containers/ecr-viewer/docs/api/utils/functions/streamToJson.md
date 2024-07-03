[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [api/utils](../README.md) / streamToJson

# Function: streamToJson()

> **streamToJson**(`stream`): `Promise`\<`any`\>

Converts stream data to json data

## Parameters

• **stream**: `any`

The input stream that provides JSON data in chunks. The stream
  should implement the async iterable protocol to allow for-await-of
  iteration over its data chunks.

## Returns

`Promise`\<`any`\>

A promise that resolves to the JSON-parsed object from the accumulated
 stream data. The specific structure of this object depends on the JSON
 content of the stream.

## Defined in

[src/app/api/utils.ts:25](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/api/utils.ts#L25)
