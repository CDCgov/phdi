/** @type {import("eslint").Linter.Config} */
module.exports = {
  parser: "@typescript-eslint/parser",
  extends: [
    "plugin:@next/next/recommended",
    "plugin:jsdoc/recommended-typescript-error",
    "prettier",
  ],
  globals: {
    React: true,
    JSX: true,
  },
  env: {
    es6: true,
  },
  plugins: ["@typescript-eslint", "unused-imports", "jsdoc"],
  ignorePatterns: [
    // Ignore dotfiles
    ".*.js",
    "node_modules/",
  ],
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
