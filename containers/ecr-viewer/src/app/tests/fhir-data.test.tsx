/**
 * @jest-environment node
 */
import fs from "fs";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { mockClient } from "aws-sdk-client-mock";
import { sdkStreamMixin } from "@smithy/util-stream";
import { getEcrData } from "@/app/api/services/ecrDataService";

const s3Mock = mockClient(S3Client);
const stream = sdkStreamMixin(
  fs.createReadStream("src/app/tests/assets/BundleTravelHistory.json"),
);

beforeEach(() => {
  s3Mock.reset();
});

const mockYamlConfig = {}; // Adjust this to match what loadYamlConfig() would return
jest.mock("../utils", () => ({
  loadYamlConfig: jest.fn().mockReturnValue(mockYamlConfig),
  streamToJson: jest.fn().mockResolvedValue({
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
  }),
}));

describe("GET API Route", () => {
  it("fetches data from S3 and returns a JSON response", async () => {
    const fakeId = "test-id";
    process.env.SOURCE = "s3";

    s3Mock
      .on(GetObjectCommand, {
        Bucket: process.env.ECR_BUCKET_NAME,
        Key: `${fakeId}.json`,
      })
      .resolves({
        Body: stream,
      });

    const response = await getEcrData(fakeId);
    expect(response).toBeDefined();
  });
});
