/* eslint-disable unused-imports/no-unused-vars */
namespace NodeJS {
  interface ProcessEnv {
    APP_ENV: "test" | "dev" | "middleware" | "prod";
    AWS_REGION: string;
    AWS_CUSTOM_ENDPOINT: string;
    AWS_ACCESS_KEY_ID: string;
    AWS_SECRET_ACCESS_KEY: string;
    AZURE_STORAGE_CONNECTION_STRING: string;
    AZURE_CONTAINER_NAME: string;
    METADATA_DATABASE_SCHEMA: "core" | "extended";
    DATABASE_TYPE: string;
    DATABASE_URL: string;
    ECR_BUCKET_NAME: string;
    GITHUB_ID: string;
    GITHUB_SECRET: string;
    NBS_PUB_KEY: string;
    NEXT_RUNTIME: string;
    NEXT_PUBLIC_NON_INTEGRATED_VIEWER: "true" | "false";
    NEXTAUTH_SECRET: string;
    SOURCE: "s3" | "azure" | "postgres";
  }
}
