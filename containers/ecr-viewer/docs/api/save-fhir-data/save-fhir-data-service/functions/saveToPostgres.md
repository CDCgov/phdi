[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [save-fhir-data/save-fhir-data-service](../README.md) / saveToPostgres

# Function: saveToPostgres()

> **saveToPostgres**(`fhirBundle`, `ecrId`): `Promise`\<`NextResponse`\<`object`\>\>

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle to be saved.

• **ecrId**: `string`

The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.

## Returns

`Promise`\<`NextResponse`\<`object`\>\>

A promise that resolves when the FHIR bundle is successfully saved to postgres.

## Defined in

[save-fhir-data/save-fhir-data-service.ts:21](https://github.com/CDCgov/phdi/blob/9949cb6cb2d0a109abb4ac696314e4046e118995/containers/ecr-viewer/src/app/api/save-fhir-data/save-fhir-data-service.ts#L21)
