[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [save-fhir-data/route](../README.md) / POST

# Function: POST()

> **POST**(`request`): `Promise`\<`NextResponse`\<`object`\>\>

Handles POST requests and saves the FHIR Bundle to the database.

## Parameters

• **request**: `NextRequest`

The incoming request object. Expected to have a JSON body in the format `{"fhirBundle":{}, "saveSource": "postgres|s3""}`. FHIR bundle must include the ecr ID under entry[0].resource.id.

## Returns

`Promise`\<`NextResponse`\<`object`\>\>

A `NextResponse` object with a JSON payload indicating the success message and the status code set to 200. The response content type is set to `application/json`.

## Defined in

[save-fhir-data/route.ts:12](https://github.com/CDCgov/phdi/blob/de911eed4d2616e3a509cdcd4c198be50c6e4315/containers/ecr-viewer/src/app/api/save-fhir-data/route.ts#L12)
