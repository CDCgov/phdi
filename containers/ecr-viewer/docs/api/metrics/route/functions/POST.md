<<<<<<< HEAD
[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [metrics/route](../README.md) / POST
=======
[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [api/metrics/route](../README.md) / POST
>>>>>>> b91b512a (docs)

# Function: POST()

> **POST**(`request`): `Promise`\<`NextResponse`\<`object`\>\>

Handles GET requests by fetching data from different sources based on the environment configuration.
It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
a supported source, it returns a JSON response indicating an invalid source.

## Parameters

• **request**: `NextRequest`

The incoming request object provided by Next.js.

## Returns

`Promise`\<`NextResponse`\<`object`\>\>

A promise that resolves to a `NextResponse` object
  if the source is invalid, or the result of fetching from the specified source.
  The specific return type (e.g., the type returned by `get_s3` or `get_postgres`)
  may vary based on the source and is thus marked as `unknown`.

## Defined in

<<<<<<< HEAD
[metrics/route.ts:14](https://github.com/CDCgov/phdi/blob/dbe13517da6c10296fb0f8b7c72a5ebb1d47f2c7/containers/ecr-viewer/src/app/api/metrics/route.ts#L14)
=======
[src/app/api/metrics/route.ts:14](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/api/metrics/route.ts#L14)
>>>>>>> b91b512a (docs)
