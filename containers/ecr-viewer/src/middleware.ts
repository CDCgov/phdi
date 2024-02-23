import { NextRequest, NextResponse } from "next/server";

export function middleware(req: NextRequest) {
  let response = NextResponse.next();
  const url = req.nextUrl;

  const auth = url.searchParams.get("auth");
  if (auth) {
    url.searchParams.delete("auth");
    response = NextResponse.redirect(url);
    response.cookies.set("auth-token", auth, { httpOnly: true });
  }

  return response;
}
