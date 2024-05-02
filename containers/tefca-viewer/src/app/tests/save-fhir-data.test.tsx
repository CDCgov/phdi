/**
 * @jest-environment node
 */

import {
  S3Client,
  PutObjectCommand,
  PutObjectCommandOutput,
} from "@aws-sdk/client-s3";
import { mockClient } from "aws-sdk-client-mock";
import { POST } from "../api/save-fhir-data/route";
import { NextRequest } from "next/server";

const s3Mock = mockClient(S3Client);
const fakeData = {
  fhirBundle: {
    resourceType: "Bundle",
    type: "batch",
    entry: [
      {
        fullUrl: "urn:uuid:12345",
        resource: {
          resourceType: "Composition",
          id: "12345",
        },
      },
    ],
  },
  saveSource: "s3",
};

beforeEach(() => {
  s3Mock.reset();
});

describe("POST Save FHIR Data API Route", () => {
  it("sends data to S3 and returns a success response", async () => {
    process.env.SOURCE = "s3";
    const request = new NextRequest(
      "http://localhost:3000/api/save-fhir-data",
      {
        method: "POST",
        body: JSON.stringify(fakeData),
      },
    );

    const output: PutObjectCommandOutput = {
      $metadata: {
        httpStatusCode: 200,
        requestId: "biz",
        extendedRequestId: "bar",
        cfId: undefined,
        attempts: 1,
        totalRetryDelay: 0,
      },
      ETag: "foo",
      ServerSideEncryption: "AES256",
    };

    s3Mock
      .on(PutObjectCommand, {
        Bucket: process.env.ECR_BUCKET_NAME,
        Key: "12345.json",
        Body: JSON.stringify(fakeData.fhirBundle),
        ContentType: "application/json",
      })
      .resolves(output);

    const response = await POST(request);
    const responseJson = await response.json();
    expect(response.status).toBe(200);
    expect(responseJson.message).toBe(
      "Success. Saved FHIR Bundle to S3: 12345",
    );
  });

  it("throws an error when bucket is not found", async () => {
    process.env.SOURCE = "s3";
    const request = new NextRequest(
      "http://localhost:3000/api/save-fhir-data",
      {
        method: "POST",
        body: JSON.stringify(fakeData),
      },
    );

    const output = {
      $fault: "client",
      $metadata: {
        httpStatusCode: 403,
        requestId: "foo",
        extendedRequestId: "foobizbarbiz",
        cfId: undefined,
        attempts: 1,
        totalRetryDelay: 0,
      },
      Code: "AllAccessDisabled",
      RequestId: "foobiz",
      HostId: "foobar",
    };

    s3Mock
      .on(PutObjectCommand, {
        Bucket: process.env.ECR_BUCKET_NAME,
        Key: "12345.json",
        Body: JSON.stringify(fakeData.fhirBundle),
        ContentType: "application/json",
      })
      .resolves(output);

    const response = await POST(request);
    const responseJson = await response.json();
    expect(response.status).toBe(400);
    expect(responseJson.message).toBe(
      "Failed to insert data to S3. HTTP Status Code: 403",
    );
  });
});
