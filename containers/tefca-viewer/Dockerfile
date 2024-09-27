FROM node:18-alpine AS base

FROM base AS builder
# Install necessary packages for building
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

# Install dependencies (bash, curl for Flyway installation)
RUN apk add --no-cache bash curl

# Install Flyway
RUN curl -L https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/10.16.0/flyway-commandline-10.16.0-linux-x64.tar.gz \
    | tar xz && \
    mv flyway-10.16.0 /flywayINSTALLER

# # Add Flyway to PATH
# ENV PATH="/flyway:$PATH"

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

# Final stage for running the app
FROM base AS runner
WORKDIR /app


# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

# Set hostname to localhost
ENV HOSTNAME "0.0.0.0"

# Copy necessary app files
COPY --from=installer /app/containers/tefca-viewer/next.config.js .
COPY --from=installer /app/containers/tefca-viewer/package.json .

# Copy Flyway from the installer stage
COPY --from=installer /flywayINSTALLER /app/flywayHERE

# Automatically leverage output traces to reduce image size
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/.next/static ./containers/tefca-viewer/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/containers/tefca-viewer/public ./containers/tefca-viewer/public

# Set environment variables for Flyway and Node.js telemetry
ENV TURBO_TELEMETRY_DISABLED=1
ENV NEXT_TELEMETRY_DISABLED=1
# ENV PATH="/flyway:$PATH"

CMD ["node", "containers/tefca-viewer/server.js"]
