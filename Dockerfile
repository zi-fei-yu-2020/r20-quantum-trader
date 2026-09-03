ARG NODE_IMAGE=node:22-alpine
ARG PYTHON_IMAGE=python:3.12-alpine

FROM ${NODE_IMAGE} AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM ${NODE_IMAGE} AS node-tools
ARG OKX_CLI_SPEC=@okx_ai/okx-trade-cli@^1.4.4
RUN npm install -g "${OKX_CLI_SPEC}"

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOME=/home/r20 \
    TZ=Asia/Shanghai \
    R20_ENV_FILE=/app/config/.env \
    NPM_CONFIG_PREFIX=/home/r20/.npm-global \
    PATH=/home/r20/.npm-global/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

WORKDIR /app
RUN apk add --no-cache libstdc++ tzdata

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=node-tools /usr/local/bin/node /usr/local/bin/node
COPY --from=node-tools /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && OKX_ENTRY="$(node -e "const p=require('/usr/local/lib/node_modules/@okx_ai/okx-trade-cli/package.json'); const b=p.bin; process.stdout.write(typeof b==='string'?b:(b.okx||Object.values(b)[0]))")" \
    && ln -s "/usr/local/lib/node_modules/@okx_ai/okx-trade-cli/${OKX_ENTRY}" /usr/local/bin/okx

RUN addgroup -g 10001 r20 \
    && adduser -D -u 10001 -G r20 -h /home/r20 -s /sbin/nologin r20

COPY --chown=r20:r20 . ./
COPY --from=frontend-builder --chown=r20:r20 /app/frontend/dist ./frontend/dist
COPY --chown=r20:r20 docker/entrypoint.sh /usr/local/bin/r20-entrypoint

# Git may check shell scripts out with CRLF on Windows. Normalize the runtime
# entrypoint so its shebang always resolves to /bin/sh inside Linux containers.
RUN sed -i 's/\r$//' /usr/local/bin/r20-entrypoint

RUN mkdir -p /app/config /app/data /app/logs /app/backups /home/r20/.okx /home/r20/.bypy /home/r20/.npm-global \
    && touch /app/config/.env \
    && chown -R r20:r20 /app/config /app/data /app/logs /app/backups /home/r20 \
    && chmod 0755 /usr/local/bin/r20-entrypoint

USER r20
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3).read()" \
    || exit 1

ENTRYPOINT ["/usr/local/bin/r20-entrypoint"]
CMD ["python", "-m", "uvicorn", "r20_backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
