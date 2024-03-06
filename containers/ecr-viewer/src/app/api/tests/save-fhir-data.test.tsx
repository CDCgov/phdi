import { POST } from "../save-fhir-data/route.ts";

const httpMocks = require("node-mocks-http");
const fhirBundle = require("./assets/testBundle.json");

function createMockRequest(body) {
  const req = httpMocks.createRequest({
    method: "POST",
    url: "/api/save-fhir-data",
    body,
  });

  req.json = async () => {
    return Promise.resolve(body);
  };

  return req;
}

describe("/api/save-fhir-data", () => {
  beforeEach(() => {
    jest.resetModules();
    jest.resetAllMocks();
  });

  test("save FHIR to database", async () => {
    jest.mock("pg-promise", () => {
      const oneMock = jest.fn(() => {
        return {
          ecr_id: "12345test",
        };
      });

      const dbMock = jest.fn((db_url) => {
        console.log("db_url:", db_url);
        return {
          one: oneMock,
        };
      });

      // const oneMockResult = {result: "success"};
      // dbMock.one.mockResolvedValue(oneMockResult);

      const pgPromiseMock = jest.fn(() => dbMock);
      return pgPromiseMock;
    });

    const body = {
      fhirBundle: fhirBundle,
    };
    const req = createMockRequest(body);

    const response = await POST(req);

    expect(response.status).toBe(200);
    expect(res.json()).toEqual({
      message: "Success. Saved FHIR Bundle to database: 12345test",
    });
  });
});
