/** @type {import('next').NextConfig} */
const path = require("path");

const nextConfig = {
  sassOptions: {
    includePaths: [
      path.join(__dirname, "node_modules", "@uswds", "uswds", "packages"),
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

  /**
   * Custom Webpack configuration to add an alias for the shared directory
   * and configure watch options for hot reloading.
   * @param config - The existing Webpack configuration.
   * @param options - Additional options provided by Next.js.
   * @param options.isServer - Indicates if the configuration is for the server-side build.
   * @returns The modified Webpack configuration.
   */
  webpack: (config, { isServer }) => {
    config.resolve.alias["@shared"] = path.resolve(__dirname, "../shared");
    if (!isServer) {
      const ignored =
        typeof config.watchOptions.ignored[Symbol.iterator] === "function"
          ? config.watchOptions.ignored
          : [config.watchOptions.ignored];

      config.watchOptions.ignored = [
        ...ignored,
        path.resolve(__dirname, "../shared"),
      ];
    }

    return config;
  },
};

module.exports = nextConfig;
