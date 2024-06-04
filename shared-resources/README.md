# Shared Modules for PHDI Containers

This folder contains shared modules that can be used across PHDI Next.js projects. Follow the instructions below to integrate these shared modules into other containers.

## Step 1: Sym link the folder to your container

From the repo you want to sym link to

Example:
```
ln -s ../../../../../shared-resources/src/ ./src/app/shared/
```

## Step 2: Install local requirements for shared-resources
In the shared resources folder run:
```
npm install
```

## Step 3: Update various build commands
Certain github build commands will need to be updated.

In order for docker to work, the files need to be located in the repo they are being used in. See these examples from build container.

```
- name: Remove symlinks (if needed)
  if: ${{ matrix.container-to-build == 'ecr-viewer' }}
  working-directory: ./containers/${{matrix.container-to-build}}/src/app/shared
  run: rm -rf ./*

- name: Copy shared-resources (if needed)
  if: ${{ matrix.container-to-build == 'ecr-viewer' }}
  working-directory: ./containers/${{matrix.container-to-build}}
  run: cp -r ../../shared-resources/src/ ./src/app/shared/
```