# Shared UI for DIBBs Containers

This folder contains shared modules that can be used across DIBBs JS projects. Follow the instructions below to add 

## Installation

Simply install `@repo/ui` using your package manager (`npm i @repo/ui`)

## Adding additional components

After a new component has been added, in order for it to be available for use it must be [added into the package.json under the `export` property](https://turbo.build/repo/docs/crafting-your-repository/structuring-a-repository#exports).

For example, after adding a new component called `Accordion` it must be added to the export in order to import it in another project.
```json
{
  "exports": {
    "./accordion": "./src/Accordion.tsx"
  }
}
```


