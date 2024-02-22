import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { importSPKI, jwtVerify } from "jose";
console.log("middleware file");
export async function middleware(request: NextRequest) {
  console.log("*** MIDDLEWARE RUNNING ****");
  const auth = request.cookies.get("authorization")?.value;
  const pathname = request.nextUrl.pathname;
  if (pathname.startsWith("/api") && !pathname.startsWith("/api/auth")) {
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
  "-----BEGIN PUBLIC KEY-----\n" +
  "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArPdvG1lKRSuWiuG54zHZ\n" +
  "IVqzC0QovDdi1/6eITdenHZeFw04x0DcjkamMwPQuIo6Q9YrqZFVblnJvQufIX8z\n" +
  "AF2FH6ga0nvvqfr2ZxSc5EAn3WKloBkUwNVlvjxuZ1pM/U8VgZOC1etl4wnrSOb3\n" +
  "Ndoh56VGQx8a0VzedxvDDBbVUglyyYik3mi68oeZoAVpRpPYFvRme3DzTfp4yNv0\n" +
  "nVRWfZIy+gCuR2bvoJYKpJ8vFqAXLhBpNBbG0/n0UnqDixfldXd6cvh4ljck35rx\n" +
  "4K31vyfIYPSA8gekNI2AOvNca2wKbYEf59lZ54WPVtO1LaimgZC6XKnnJ58WVd5M\n" +
  "957Gh5aFRBWw8WwQVeHa49ufBW+XeNoSRNFfEtKtabp9rwGYoP4Rg1j/aYhZGcee\n" +
  "5QULx03PyqRaKBE7rPgLX9Bcyo3KEOsjDvkcQLBu7zmquDxYI7CrtVyEPKhS86aW\n" +
  "LgGekg5HOjYRsPTVyHDFckkPzFy8zL9cg6YFLBUbYIB6KX2+t6phVViUmlFehRCK\n" +
  "xD78YuDEqGUyLGsCb/ZLTRrRY90vr7SCDewlMs2/U7IKwQxa5dZH+OpnqpKPWifc\n" +
  "ZEgkUrV9Zf5dacRLyYZCNWNZxXtSkBxKuMr28N7dVrAs8vi4r/s7vbl0q99aseXU\n" +
  "3YsIKWOnoXcaVh8KMZ5OomkCAwEAAQ==\n" +
  "-----END PUBLIC KEY-----";
