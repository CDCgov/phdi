[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [api/services/listEcrDataService](../README.md) / listEcrData

# Function: listEcrData()

> **listEcrData**(): `Promise`\<[`ListEcr`](../type-aliases/ListEcr.md)\>

Handles GET requests by fetching data from different sources based on the environment configuration.
It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
a supported source, it returns a JSON response indicating an invalid source.

## Returns

`Promise`\<[`ListEcr`](../type-aliases/ListEcr.md)\>

A promise that resolves to a `NextResponse` object
  if the source is invalid, or the result of fetching from the specified source.
  The specific return type (e.g., the type returned by `list_s3` or `list_postgres`)
  may vary based on the source and is thus marked as `unknown`.

## Defined in

[src/app/api/services/listEcrDataService.ts:31](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/api/services/listEcrDataService.ts#L31)
