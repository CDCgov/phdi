import { NextRequest, NextResponse } from "next/server";
import { importSPKI, jwtVerify } from "jose";

export async function middleware(req: NextRequest): Promise<NextResponse> {
  return (
    set_auth_cookie(req) ?? (await authorize_api(req)) ?? NextResponse.next()
  );
}

export const config = {
  matcher: ["/api/:path*", "/view-data"],
};

function set_auth_cookie(req: NextRequest) {
  const url = req.nextUrl;
  const auth = url.searchParams.get("auth");
  if (auth) {
    url.searchParams.delete("auth");
    const response = NextResponse.redirect(url);
    response.cookies.set("auth-token", auth, { httpOnly: true });
    return response;
  }
  return null;
}

async function authorize_api(req: NextRequest) {
  const auth = req.cookies.get("auth-token")?.value;
  const pathname = req.nextUrl.pathname;
  const isDevelopment = process.env.NODE_ENV === "development";
  if (!isDevelopment && pathname.startsWith("/api")) {
    if (!auth) {
      return NextResponse.json({ message: "Auth required" }, { status: 401 });
    }
    try {
      await jwtVerify(
        auth,
        await importSPKI(process.env.NBS_PUB_KEY as string, "RS256"),
      );
    } catch (e) {
      return NextResponse.json({ message: "Auth required" }, { status: 401 });
    }
    return NextResponse.next();
  }
  return null;
}
