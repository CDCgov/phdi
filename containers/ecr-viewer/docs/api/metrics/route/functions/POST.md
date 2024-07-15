[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [metrics/route](../README.md) / POST

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

[metrics/route.ts:14](https://github.com/CDCgov/phdi/blob/de911eed4d2616e3a509cdcd4c198be50c6e4315/containers/ecr-viewer/src/app/api/metrics/route.ts#L14)
