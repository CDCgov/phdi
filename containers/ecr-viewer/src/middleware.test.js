/**
 * @jest-environment node
 */
import { middleware } from "@/middleware";
import { NextRequest } from "next/server";
import { importSPKI, jwtVerify } from "jose";
import { getToken } from "next-auth/jwt";

jest.mock("jose", () => ({
  importSPKI: jest.fn(() => true),
  jwtVerify: jest.fn(() => true),
}));

// Mock next-auth/jwt getToken
jest.mock("next-auth/jwt", () => ({
  getToken: jest.fn(),
}));

describe("Middleware", () => {
  beforeEach(() => {
    process.env.NEXTAUTH_SECRET = "test-secret";
    process.env.APP_ENV = "middleware";
    jest.resetAllMocks(); // Reset mocks before each test
  });

  it("should authorize the request if oauthToken is present", async () => {
    getToken.mockImplementation(() => Promise.resolve({ token: "fake-token" }));

    const req = new NextRequest("https://www.example.com/api/protected");

    const resp = await middleware(req);

    expect(resp.status).toBe(200);
    expect(getToken).toHaveBeenCalledWith({
      req,
      secret: process.env.NEXTAUTH_SECRET,
    });
  });

  it("should strip the auth query param and set the token", async () => {
    const req = new NextRequest(
      "https://www.example.com/api?id=1234&auth=abcd",
    );

    const resp = await middleware(req);
    expect(resp.cookies.get("auth-token")).toEqual({
      name: "auth-token",
      path: "/",
      value: "abcd",
      httpOnly: true,
    });
    expect(resp.headers.get("location")).toBe(
      "https://www.example.com/api?id=1234",
    );
  });

  it("should not authorize the api endpoints without auth", async () => {
    const req = new NextRequest("https://www.example.com/api/fhir-data/");

    const resp = await middleware(req);
    const respJson = await resp.json();
    expect(respJson.message).toBe("Auth required");
    expect(resp.status).toBe(401);
  });

  it("should authorize the api endpoints with auth", async () => {
    process.env.NBS_PUB_KEY = "FOOBAR";

    const req = new NextRequest("https://www.example.com/api/fhir-data/");
    req.cookies.set("auth-token", "foobar");

    const resp = await middleware(req);

    expect(jwtVerify).toHaveBeenCalled();
    expect(importSPKI).toHaveBeenCalledWith("FOOBAR", "RS256");
    expect(resp.status).toBe(200);
  });

  it("should not authorize non api endpoints ", async () => {
    const req = new NextRequest("https://www.example.com/view-data?id=1234");
    const resp = await middleware(req);
    expect(resp.status).toBe(401);
  });
});
