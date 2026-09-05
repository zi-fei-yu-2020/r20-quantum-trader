# Both stages use Debian/bookworm so the copied Node binary matches runtime libc.
ARG NODE_IMAGE=node:22-bookworm-slim
ARG PYTHON_IMAGE=python:3.12-slim-bookworm

FROM ${NODE_IMAGE} AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Keep the server's documentation-image deployment fix in version control.
COPY docs/images/ ./public/images/
RUN npm run build

FROM ${PYTHON_IMAGE} AS runner
ARG OKX_CLI_SPEC=@okx_ai/okx-trade-cli@^1.4.4
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    R20_DOCKER=1 \
    R20_DEPLOYMENT_MODE=docker \
    R20_ENV_FILE=/app/config/.env \
    PORT=8080 \
    HOME=/home/r20

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl procps git libstdc++6 tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY --from=frontend-builder /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend-builder /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && npm install --global "${OKX_CLI_SPEC}" \
    && npm cache clean --force \
    && node --version && okx --version
# Optional administrator CLI upgrades live on the existing npm volume, while
# the image always contains a working CLI even when that volume is empty.
ENV NPM_CONFIG_PREFIX=/home/r20/.npm-global \
    PATH=/home/r20/.npm-global/bin:${PATH}

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY r20_backend/ ./r20_backend/
COPY r20_gateway/ ./r20_gateway/
COPY scripts/ ./scripts/
COPY plugins/ ./plugins/
COPY dashboard/ ./dashboard/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY README.md STANDALONE.md env.example ./
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY docker/entrypoint.sh /usr/local/bin/r20-entrypoint
RUN sed -i 's/\r$//' /usr/local/bin/r20-entrypoint \
    && chmod +x /usr/local/bin/r20-entrypoint \
    && mkdir -p /app/config /app/data /app/logs /app/backups

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/api/v1/health || exit 1
ENTRYPOINT ["/usr/local/bin/r20-entrypoint"]
CMD ["python", "-m", "uvicorn", "r20_backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
