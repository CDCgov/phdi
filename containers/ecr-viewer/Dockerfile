FROM node:18-alpine AS base

FROM base AS builder
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk update
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app
RUN npm i -g turbo
COPY . .
RUN turbo prune ecr-viewer --docker

# Add lockfile and package.json's of isolated subworkspace
FROM base AS installer
RUN apk update
RUN apk add --no-cache libc6-compat
WORKDIR /app

# First install the dependencies (as they change less often)
COPY .gitignore .gitignore
COPY --from=builder /app/out/json/ .
COPY --from=builder /app/out/package-lock.json ./package-lock.json
RUN npm i

# Build the project
COPY --from=builder /app/out/full/ .
COPY turbo.json turbo.json
ENV NEXT_TELEMETRY_DISABLED=1

RUN npx turbo build --filter=ecr-viewer...

FROM base AS runner
WORKDIR /app

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

COPY --from=installer /app/containers/ecr-viewer/next.config.js .
COPY --from=installer /app/containers/ecr-viewer/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/containers/ecr-viewer/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/containers/ecr-viewer/.next/static ./containers/ecr-viewer/.next/static
#COPY --from=installer --chown=nextjs:nodejs /app/containers/ecr-viewer/public ./containers/ecr-viewer/public

ENV NEXT_TELEMETRY_DISABLED=1
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=none

# Prometheus preferred transfer is via HTTP
ENV OTEL_EXPORTER_OTLP_METRICS_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://otel-collector:4318/v1/metrics

# Jaeger preferred routing is gRPC for native OTLP
ENV OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=grpc
# Contrary to orchestration, this must be 4318
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://otel-collector:4318/v1/traces

CMD ["node", "containers/ecr-viewer/server.js"]