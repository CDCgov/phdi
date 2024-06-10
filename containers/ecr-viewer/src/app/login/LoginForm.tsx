"use client"; // Indicates that this module is client-side code.

import { Button } from "@trussworks/react-uswds";
import { signIn } from "next-auth/react"; // Import the signIn function from NextAuth for authentication.

/**
 * @returns a button
 */
export const LoginForm = () => {
  return (
    <Button type="button" onClick={() => signIn("github")}>
      Sign in with Github
    </Button>
  );
};
