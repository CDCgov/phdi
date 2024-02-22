import { createRequest } from "node-mocks-http";
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
  test("save FHIR to database", async () => {
    const body = {
      fhirBundle: fhirBundle,
    };
    const req = createMockRequest(body);

    const response = await POST(req);

    expect(response.status).toBe(200);
    // expect(res.json()).toEqual({
    //   message: "Success. Saved FHIR Bundle to database: 1dd10047-2207-4eac-a993-0f706c88be5d"
    // });
  });
});

// import { POST } from "../save-fhir-data/route.ts";
// import pgPromise from "pg-promise";
// import { NextRequest, NextResponse } from "next/server";

// const pgPromiseMock = jest.mock("pg-promise");
// // pgPromiseMock.one.mockReturnValue = NextResponse.json(
// //   { message: "Success. Saved FHIR Bundle to database" },
// //   { status: 200 },
// // );

// const fhirBundle = require("./assets/testBundle.json");
// const request: NextRequest = {
//   fhirBundle: fhirBundle,
// };

// describe("Test saving FHIR bundle to database", () => {
//   beforeEach(() => {
//     jest.resetModules();
//     jest.resetAllMocks();
//   });

//   it("should call pg-promise with an ecr ID and a FHIR bundle when endpoint is hit", () => {
//     const result = POST(request);

//     console.log(pgPromiseMock);
//     // expect(pgPromiseMock).toHaveBeenCalledWith(1, 2);
//   });
// });

// import * as app from "./app";
// import * as math from "./math";

// // Set all module functions to jest.fn
// jest.mock("./math.js");

// test("calls math.add", () => {
//   app.doAdd(1, 2);
//   expect(math.add).toHaveBeenCalledWith(1, 2);
// });

// test("calls math.subtract", () => {
//   app.doSubtract(1, 2);
//   expect(math.subtract).toHaveBeenCalledWith(1, 2);
// });
