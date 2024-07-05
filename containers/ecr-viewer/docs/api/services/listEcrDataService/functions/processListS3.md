[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [api/services/listEcrDataService](../README.md) / processListS3

# Function: processListS3()

> **processListS3**(`responseBody`): [`ListEcr`](../type-aliases/ListEcr.md)

## Parameters

• **responseBody**: `ListObjectsV2CommandOutput`

The response body containing eCR data from S3.

## Returns

[`ListEcr`](../type-aliases/ListEcr.md)

- The processed list of eCR IDs and dates.

## Defined in

[src/app/api/services/listEcrDataService.ts:106](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/api/services/listEcrDataService.ts#L106)
