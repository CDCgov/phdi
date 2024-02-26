/**
 * @jest-environment node
 */
import { middleware } from "@/middleware";
import { NextRequest } from "next/server";

describe("Middleware", () => {
  it("should strip the auth query param and set the token", async () => {
    const req = new NextRequest(
      "https://www.example.com/view-data?id=1234&auth=abcd",
    );

    const resp = await middleware(req);
    expect(resp.cookies.get("auth-token")).toEqual({
      name: "auth-token",
      path: "/",
      value: "abcd",
      httpOnly: true,
    });
    expect(resp.headers.get("location")).toBe(
      "https://www.example.com/view-data?id=1234",
    );
  });

  it("should authorize the api endpoints", async () => {
    const req = new NextRequest("https://www.example.com/api/fhir-data/");

    const resp = await middleware(req);
    const respJson = await resp.json();
    expect(respJson.message).toBe("Auth required");
    expect(resp.status).toBe(401);
  });

  it("should not authorize non api endpoints ", async () => {
    const req = new NextRequest("https://www.example.com/view-data?id=1234");
    const resp = await middleware(req);
    expect(resp.status).toBe(200);
  });
});
