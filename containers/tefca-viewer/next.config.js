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
  transpilePackages: ["yaml"],
  async rewrites() {
    return [
      {
        source: "/tefca-viewer/:slug*",
        destination: "/:slug*",
      },
    ];
  },
  output: "standalone",
  basePath: process.env.NODE_ENV === "production" ? "/tefca-viewer" : "",
};

module.exports = nextConfig;
