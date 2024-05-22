# Shared Modules for PHDI Containers

This folder contains shared modules that can be used across PHDI Next.js projects. Follow the instructions below to integrate these shared modules into other containers.

## Step 1: Configure TypeScript in the PHDI container

Update the `tsconfig.json` file to include the shared folder in the module resolution paths.

### tsconfig.json

Add the following configuration:

**container/tsconfig.json**

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@shared/*": ["../shared/src/*"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    "../shared"
  ]
}
```

## Step 2: Configure Webpack in next.config.js

Update the next.config.js file in your PHDI container to resolve the @shared alias.

```json
const path = require('path');

module.exports = {
  webpack: (config, { isServer }) => {
    config.resolve.alias['@shared'] = path.resolve(__dirname, '../shared');
    if (!isServer) {
      const ignored = typeof config.watchOptions.ignored[Symbol.iterator] === "function" ? 
        config.watchOptions.ignored : [config.watchOptions.ignored];
      
      config.watchOptions.ignored = [
        ...ignored,
        path.resolve(__dirname, '../shared')
      ];
    }

    return config;
  },
};
```

## Step 3: Import Shared Modules
You can now import the shared modules in your PHDI container using the `@shared` alias.

```
// pages/index.tsx
import sharedModule from '@shared/module';

const HomePage = () => {
  sharedModule();
  return <div>Home Page using shared module</div>;
};

export default HomePage;
```