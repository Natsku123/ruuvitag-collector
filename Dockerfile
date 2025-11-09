FROM python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --compile-bytecode

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --compile-bytecode

FROM python:3.13-slim-trixie

LABEL maintainer="Max Mecklin <max@meckl.in>"

RUN apt-get update && \
    apt-get -y --no-install-recommends install musl-dev sudo bluez dbus bluez-hcidump && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/docker-entrypoint.sh /app/docker-entrypoint.sh

RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["/app/.venv/bin/main"]