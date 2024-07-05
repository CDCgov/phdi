[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [api/save-fhir-data/save-fhir-data-service](../README.md) / saveToS3

# Function: saveToS3()

> **saveToS3**(`fhirBundle`, `ecrId`): `Promise`\<`NextResponse`\<`object`\>\>

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle to be saved.

• **ecrId**: `string`

The unique identifier for the Electronic Case Reporting (ECR) associated with the FHIR bundle.

## Returns

`Promise`\<`NextResponse`\<`object`\>\>

A promise that resolves when the FHIR bundle is successfully saved to the S3 bucket.

## Defined in

[src/app/api/save-fhir-data/save-fhir-data-service.ts:57](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/api/save-fhir-data/save-fhir-data-service.ts#L57)
