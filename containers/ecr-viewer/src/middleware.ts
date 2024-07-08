import { NextRequest, NextResponse } from "next/server";
import { importSPKI, jwtVerify } from "jose";
import { getToken } from "next-auth/jwt";

/**
 * Acts as a middleware for handling authentication and authorization in a Next.js application.
 * @param req - The incoming request object provided by Next.js.
 * @returns A promise that resolves to a `NextResponse` object, which could
 *     be a redirection, an error response, or a signal to proceed to the next middleware or page
 *     handler based on the authentication and authorization logic.
 */
export async function middleware(req: NextRequest): Promise<NextResponse> {
  const isDevelopment = process.env.NODE_ENV === "development";
  const isTest = process.env.APP_ENV === "test";
  const needsAuth = !isDevelopment && !isTest;

  const oauthToken = await getToken({
    req,
    secret: process.env.NEXTAUTH_SECRET,
  });
  if (needsAuth) {
    if (oauthToken) {
      return NextResponse.next();
    } else {
      const nbsAuth = set_auth_cookie(req) ?? (await authorize_api(req));
      if (nbsAuth) {
        return nbsAuth;
      } else {
        return NextResponse.json({ message: "Auth required" }, { status: 401 });
      }
    }
  } else {
    return NextResponse.next();
  }
}

export const config = {
  matcher: ["/api/fhir-data", "/api/metrics", "/view-data", "/"],
};

/**
 * Extracts an authentication token from the query parameters of a request and sets it as an HTTP-only
 * cookie on a response object.
 * @param req - The incoming request object provided by Next.js, containing the URL from
 *   which the "auth" query parameter will be extracted.
 * @returns A Next.js response object configured to redirect the user and set the
 *   "auth-token" cookie if the "auth" parameter exists, or `null` if the
 *   "auth" parameter does not exist in the request.
 */
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

/**
 * Authorizes API requests based on an authentication token provided in the request's cookies.
 *   The function checks for the presence of an "auth-token" cookie and attempts to verify it
 *   using JWT verification with a public key. If the token is missing or invalid, the function
 *   returns a JSON response indicating that authentication is required with a 401 status code.
 * @param req - The incoming Next.js request object, which includes the request cookies
 *   and URL information used for extracting the authentication token and determining the request path.
 * @returns - A Next.js response object configured to return a 401 status with an
 *   "Auth required" message if authentication fails or is required. Returns `NextResponse.next()` to
 *   continue to the next middleware or handler if authentication succeeds. Returns `null` to indicate
 *   no action is taken by this middleware for non-applicable routes or in development mode.
 */
async function authorize_api(req: NextRequest) {
  const auth = req.cookies.get("auth-token")?.value;

  if (!auth) {
    return null;
  }
  try {
    await jwtVerify(
      auth,
      await importSPKI(process.env.NBS_PUB_KEY as string, "RS256"),
    );
  } catch (e) {
    return null;
  }
  return NextResponse.next();
}
