import NextAuth from "next-auth/next";
import GitHubProvider from "next-auth/providers/github";

const handler = NextAuth({
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_ID,
      clientSecret: process.env.GITHUB_SECRET,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  callbacks: {
    async redirect({ baseUrl }) {
      // Ensure you are redirecting to the right baseUrl
      return baseUrl;
    },
  },
});

export { handler as GET, handler as POST };
