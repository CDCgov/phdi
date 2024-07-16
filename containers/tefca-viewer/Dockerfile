FROM node:18-alpine AS base

FROM base AS builder
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk update
RUN apk add --no-cache libc6-compat curl

# Set working directory 
WORKDIR /app
RUN npm i -g turbo
COPY . .
ENV TURBO_TELEMETRY_DISABLED=1
RUN turbo prune tefca-viewer --docker

# Add lockfile and package.json's of isolated subworkspace
FROM base AS installer
RUN apk update
RUN apk add --no-cache libc6-compat
WORKDIR /app

# First install the dependencies
COPY .gitignore .gitignore
COPY --from=builder /app/out/json/ .
COPY --from=builder /app/out/package-lock.json ./package-lock.json
RUN npm i

# Build the project
COPY --from=builder /app/out/full/ .
COPY turbo.json turbo.json
ENV TURBO_TELEMETRY_DISABLED=1

RUN npx turbo build --filter=tefca-viewer...

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
# ENV NEXT_TELEMETRY_DISABLED 1

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

COPY --from=installer /app/containers/tefca-viewer/next.config.js .
COPY --from=installer /app/containers/tefca-viewer/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/static ./containers/tefca-viewer/.next/static

EXPOSE 3000
EXPOSE 8080

ENV PORT 3000
# set hostname to localhost
ENV HOSTNAME "0.0.0.0"

ENV NODE_TLS_REJECT_UNAUTHORIZED "0"
# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD ["node", "containers/tefca-viewer/server.js"]



# FROM hapiproject/hapi:latest

# # Copy the application files to the container
# COPY ./src/app/tests/assets/BundleHAPIServer.json /app/BundleHAPIServer.json

# # Run the server
# CMD ["node", "server.js", "sh","curl", "-X", "POST", "--data", "@app/BundleHAPIServer.json", "--header", "Content-Type: application/json", "http://localhost:8080/fhir"]