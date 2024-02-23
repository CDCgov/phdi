/**
 * @jest-environment node
 */
import { middleware } from "@/middleware";
import { NextRequest, NextResponse } from "next/server";
import { NextURL } from "next/dist/server/web/next-url";

describe("Middleware", () => {
  const redirectSpy = jest.spyOn(NextResponse, "redirect");

  afterEach(() => {
    redirectSpy.mockReset();
  });
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
    expect(redirectSpy).toHaveBeenCalledTimes(1);
    expect(redirectSpy as unknown as NextURL).toHaveBeenCalledWith(
      new NextURL("view-data?id=1234", req.url, {
        headers: {},
        nextConfig: undefined,
      }),
    );
  });
});
