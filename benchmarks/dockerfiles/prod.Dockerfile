# syntax=docker/dockerfile:1.7
# Production recipe: combines what worked in the three contest recipes.
#  - multi-stage, build tools never reach runtime        (TOP 1, TOP 2)
#  - manifest/lock before source -> cache survives edits  (TOP 1)
#  - Alpine runtime for size                              (TOP 2)
#  - strip shared libraries inside the builder           (TOP 2)
#  - hashed lock + wheels only -> reproducible, no compiler (new)
#  - working uv cache mount, files owned by root, non-root user (new)

ARG PYTHON_IMAGE=python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8

FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv

FROM ${PYTHON_IMAGE} AS builder
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never
RUN apk add --no-cache binutils \
 && uv venv /opt/venv
# Lock is the only input of this step, so editing src/ never re-runs it.
COPY benchmarks/prod/requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv/bin/python \
        --require-hashes --no-build -r /tmp/requirements.txt \
 && find /opt/venv -name '*.so' -exec strip --strip-unneeded {} +

FROM ${PYTHON_IMAGE} AS runtime
LABEL org.opencontainers.image.title="python-service-template" \
      org.opencontainers.image.source="https://github.com/newnol/DockerFile-Contest"
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    HOST=0.0.0.0 \
    PORT=5000 \
    WORKERS=1
RUN addgroup -g 10001 -S app \
 && adduser -u 10001 -S -G app -H -h /app -s /sbin/nologin app
WORKDIR /app
# Owned by root: the app user can read and execute but not modify its code or libraries.
COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/
USER 10001:10001
EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${PORT}/health/', timeout=2)" || exit 1
STOPSIGNAL SIGTERM
CMD ["python", "src/python_service_template/app.py"]
