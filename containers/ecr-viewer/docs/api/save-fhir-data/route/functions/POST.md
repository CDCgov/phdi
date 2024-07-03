<<<<<<< HEAD
[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [save-fhir-data/route](../README.md) / POST
=======
[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [api/save-fhir-data/route](../README.md) / POST
>>>>>>> b91b512a (docs)

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

<<<<<<< HEAD
[save-fhir-data/route.ts:12](https://github.com/CDCgov/phdi/blob/dbe13517da6c10296fb0f8b7c72a5ebb1d47f2c7/containers/ecr-viewer/src/app/api/save-fhir-data/route.ts#L12)
=======
[src/app/api/save-fhir-data/route.ts:12](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/api/save-fhir-data/route.ts#L12)
>>>>>>> b91b512a (docs)
