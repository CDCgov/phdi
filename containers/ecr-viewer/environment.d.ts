/* eslint-disable unused-imports/no-unused-vars */
namespace NodeJS {
  interface ProcessEnv {
    APP_ENV: "test" | "dev" | "middleware" | "prod";
    AWS_ACCESS_KEY_ID: string;
    AWS_CUSTOM_ENDPOINT: string;
    AWS_REGION: string;
    AWS_SECRET_ACCESS_KEY: string;
    AZURE_CONTAINER_NAME: string;
    AZURE_STORAGE_CONNECTION_STRING: string;
    DATABASE_TYPE: string;
    DATABASE_URL: string;
    ECR_BUCKET_NAME: string;
    GITHUB_ID: string;
    GITHUB_SECRET: string;
    METADATA_DATABASE_SCHEMA: "core" | "extended";
    METADATA_DATABASE_TYPE: "postgres" | "sqlserver";
    NBS_PUB_KEY: string;
    NEXT_PUBLIC_NON_INTEGRATED_VIEWER: "true" | "false";
    NEXT_RUNTIME: string;
    NEXTAUTH_SECRET: string;
    SOURCE: "s3" | "azure" | "postgres";
    SQL_SERVER_HOST: string;
    SQL_SERVER_PASSWORD: string;
    SQL_SERVER_USER: string;
  }
}
