/**
 * @jest-environment node
 */
import fs from "fs";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { mockClient } from "aws-sdk-client-mock";
import { GET } from "../api/fhir-data/route"; // Adjust the import path to your actual file path
import { sdkStreamMixin } from "@smithy/util-stream";
import { NextRequest } from "next/server";
import { Readable } from "stream";

const s3Mock = mockClient(S3Client);
const stream = sdkStreamMixin(
  fs.createReadStream("src/app/tests/assets/BundleTravelHistory.json"),
);

const mockYamlConfig = {}; // Adjust this to match what loadYamlConfig() would return
const mockData = {
  resourceType: "Bundle",
  type: "batch",
  entry: [
    {
      fullUrl: "urn:uuid:1dd10047-2207-4eac-a993-0f706c88be5d",
      resource: {
        resourceType: "Composition",
        id: "1dd10047-2207-4eac-a993-0f706c88be5d",
      },
    },
  ],
};

jest.mock("../view-data/utils/utils", () => ({
  loadYamlConfig: jest.fn().mockReturnValue(mockYamlConfig),
  streamToJson: jest.fn().mockResolvedValue(mockData),
}));
jest.mock("@azure/storage-blob", () => ({
  BlobServiceClient: {
    fromConnectionString: jest.fn(() => mockBlobServiceClient),
  },
}));

const mockStream = new Readable({
  read() {
    this.push(JSON.stringify(mockData));
    this.push(null);
  },
});
const mockBlobClient = {
  download: jest.fn().mockResolvedValue({
    readableStreamBody: mockStream,
  }),
};
const mockContainerClient = {
  getBlobClient: jest.fn(() => mockBlobClient),
};
const mockBlobServiceClient = {
  getContainerClient: jest.fn(() => mockContainerClient),
};

describe("GET API Route", () => {
  it("fetches data from S3 and returns a JSON response", async () => {
    const fakeId = "test-id";
    process.env.SOURCE = "s3";
    const request = new NextRequest(`http://localhost?id=${fakeId}`);

    s3Mock
      .on(GetObjectCommand, {
        Bucket: process.env.ECR_BUCKET_NAME,
        Key: `${fakeId}.json`,
      })
      .resolves({
        Body: stream,
      });

    const response = await GET(request);
    expect(response.status).toBe(200);
    const jsonResponse = await response.json();
    expect(jsonResponse.fhirBundle).toBeDefined();
  });

  it("fetches data from Azure Blob Storage and returns a JSON response", async () => {
    const fakeId = "test-id";
    process.env.SOURCE = "azure";
    const request = new NextRequest(`http://localhost?id=${fakeId}`);

    const response = await GET(request);
    expect(response.status).toBe(200);
    const jsonResponse = await response.json();
    expect(jsonResponse.fhirBundle).toBeDefined();
    expect(jsonResponse.fhirBundle).toEqual(mockData);
  });

  it("Throws an error when an invalid source is provided", async () => {
    const fakeId = "test-id";
    process.env.SOURCE = "bad-source";
    const request = new NextRequest(`http://localhost?id=${fakeId}`);

    const response = await GET(request);
    expect(response.status).toBe(500);
    const jsonResponse = await response.json();
    expect(jsonResponse.message).toBe("Invalid source");
  });
});
