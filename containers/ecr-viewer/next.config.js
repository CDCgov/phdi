/** @type {import('next').NextConfig} */
const path = require("path");

const nextConfig = {
  sassOptions: {
    includePaths: [
      path.join(
        __dirname,
        "../..",
        "node_modules",
        "@uswds",
        "uswds",
        "packages",
      ),
    ],
  },
  experimental: {
    instrumentationHook: true, // this needs to be here for opentelemetry
  },
  transpilePackages: ["yaml"],
  async rewrites() {
    return [
      {
        source: "/ecr-viewer/:slug*",
        destination: "/:slug*",
      },
    ];
  },
  output: "standalone",
  basePath: process.env.NODE_ENV === "production" ? "/ecr-viewer" : "",
};

module.exports = nextConfig;
