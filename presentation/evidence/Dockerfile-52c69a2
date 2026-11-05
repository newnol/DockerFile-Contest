# syntax=docker/dockerfile:1.7
# Build context: decolua/9router at cebc72e3438dca5aad69b2828cb0d0f2e54b168d
FROM cgr.dev/chainguard/wolfi-base@sha256:771146c2dfc880902a185f060c3db5571473c46b267edd98c3119c83068dfb61 AS base
RUN apk add --no-cache nodejs-22
WORKDIR /app

FROM base AS builder
RUN apk add --no-cache npm build-base python-3
COPY package.json ./
RUN --mount=type=cache,target=/root/.npm npm install --include=dev
COPY . ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN --mount=type=cache,target=/root/.npm \
    npm install-scripts approve better-sqlite3 && npm rebuild better-sqlite3
RUN npm run build
# Match upstream's lazy runtime dependencies, omitted by Next file tracing.
RUN --mount=type=cache,target=/root/.npm \
    mkdir -p /opt/lazy-runtime && cd /opt/lazy-runtime && \
    npm init -y >/dev/null && npm install --no-save wreq-js playwright-core

FROM base AS runner
RUN apk add --no-cache ffmpeg libstdc++ && \
    mkdir -p /app/data /app/data-home && chown -R nonroot:nonroot /app
ENV NODE_ENV=production PORT=20128 HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1 DATA_DIR=/app/data HOME=/app/data-home
LABEL org.opencontainers.image.title="9router-wolfi" \
      org.opencontainers.image.version="0.4.41" \
      org.opencontainers.image.source="https://github.com/decolua/9router" \
      org.opencontainers.image.revision="cebc72e3438dca5aad69b2828cb0d0f2e54b168d"
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/open-sse ./open-sse
COPY --from=builder /app/src/mitm ./src/mitm
COPY --from=builder /app/node_modules/node-forge ./node_modules/node-forge

COPY --from=builder /app/node_modules/sql.js ./node_modules/sql.js
COPY --from=builder /app/node_modules/node-machine-id ./node_modules/node-machine-id
COPY --from=builder /opt/lazy-runtime/node_modules/. ./node_modules/
USER nonroot
EXPOSE 20128
HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:20128/api/health').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"
CMD ["node", "server.js"]
