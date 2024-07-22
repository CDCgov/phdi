FROM node:18-alpine AS base

FROM base AS builder
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk update
RUN apk add --no-cache libc6-compat

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
ENV NEXT_TELEMETRY_DISABLED=1
ENV TURBO_TELEMETRY_DISABLED=1

RUN npx turbo build --filter=tefca-viewer...

FROM base AS runner
WORKDIR /app

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

# Set hostname to localhost
ENV HOSTNAME "0.0.0.0"

COPY --from=installer /app/containers/tefca-viewer/next.config.js .
COPY --from=installer /app/containers/tefca-viewer/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/static ./containers/tefca-viewer/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/public ./containers/tefca-viewer/public

ENV TURBO_TELEMETRY_DISABLED=1
ENV NEXT_TELEMETRY_DISABLED=1


CMD ["node", "containers/tefca-viewer/server.js"]
