import POST from "../save-fhir-data/route.ts";
import pgPromise from "pg-promise";
import { NextRequest, NextResponse } from "next/server";

const pgPromiseMock = jest.mock("pg-promise");
pgPromiseMock.one.mockReturnValue = NextResponse.json(
  { message: "Success. Saved FHIR Bundle to database" },
  { status: 200 },
);

const fhirBundle = require("./assets/testBundle.json");
const request: NextRequest = {
  fhirBundle: fhirBundle,
};

describe("Test saving FHIR bundle to database", () => {
  beforeEach(() => {
    jest.resetModules();
    jest.resetAllMocks();
  });

  it("should call pg-promise with an ecr ID and a FHIR bundle when endpoint is hit", () => {
    const result = POST(request);

    expect(pgPromise.one).toHaveBeenCalledWith(1, 2);
  });
});

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
