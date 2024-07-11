/** @type {import("eslint").Linter.Config} */
module.exports = {
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "unused-imports", "jsdoc"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:jsdoc/recommended-typescript-error",
    "prettier",
  ],
  globals: {
    React: true,
    JSX: true,
  },
  env: {
    browser: true,
  },
  ignorePatterns: [".*.js", "node_modules/", "dist/"],
  rules: {
    "no-unused-vars": "off",
    "unused-imports/no-unused-imports": "error",
    "unused-imports/no-unused-vars": [
      "warn",
      {
        vars: "all",
        varsIgnorePattern: "^_",
        args: "after-used",
        argsIgnorePattern: "^_",
      },
    ],
    "jsdoc/check-tag-names": "off",
    "jsdoc/require-jsdoc": [
      "error",
      {
        require: {
          ArrowFunctionExpression: true,
        },
        publicOnly: true,
      },
    ],
  },
  overrides: [
    {
      files: ["*.test*", "**/tests/**/*"],
      rules: {
        "jsdoc/require-jsdoc": "off",
      },
    },
  ],
};
