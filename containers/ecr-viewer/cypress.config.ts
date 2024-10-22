import { defineConfig } from "cypress";

const isDev = process.env.NODE_ENV === "dev";
export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: `http://127.0.0.1:3000`,
    env: {
      BASE_PATH: `${isDev ? "/" : "/ecr-viewer"}`,
    },
    defaultCommandTimeout: 120000,
  },
  video: true,
});
