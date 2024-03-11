/**
 * @jest-environment node
 */

import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
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
    console.log("*****", process.env.ECR_BUCKET_NAME);
    s3Mock
      .on(PutObjectCommand, {
        Bucket: process.env.ECR_BUCKET_NAME,
        Key: "test-ecrid.json",
        Body: JSON.stringify(fakeData),
        ContentType: "application/json",
      })
      .resolves({
        // mock response from S3?
      });

    const response = await POST(request);
    expect(response.status).toBe(200);
  });
});
