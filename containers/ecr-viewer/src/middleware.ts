import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { importSPKI, jwtVerify } from "jose";
export async function middleware(request: NextRequest) {
  const auth = request.cookies.get("authorization")?.value;
  const pathname = request.nextUrl.pathname;
  const isDevelopment = process.env.NODE_ENV === "development" || false;
  console.log("isDevelopment", isDevelopment);
  console.log("process.env.NODE_ENV", process.env.NODE_ENV);
  if (
    !isDevelopment &&
    pathname.startsWith("/api") &&
    !pathname.startsWith("/api/auth")
  ) {
    if (!auth) {
      return NextResponse.redirect(new URL("/404", request.url));
    }
    try {
      await jwtVerify(auth, await importSPKI(publickey, "RS256"));
    } catch (e) {
      return NextResponse.json({ message: "Auth required" }, { status: 401 });
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/api/:path*"],
};

const publickey =
  "-----BEGIN PUBLIC KEY-----\n" + "PLACEHOLDER\n" + "-----END PUBLIC KEY-----";
