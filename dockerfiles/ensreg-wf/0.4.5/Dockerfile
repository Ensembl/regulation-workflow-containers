# Standalone Python build with multistage images.

ARG PYTHON_VERSION
ARG SOFTWARE_VERSION

# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:0.10-python${PYTHON_VERSION}-trixie-slim AS builder
ARG PYTHON_VERSION
ARG SOFTWARE_VERSION
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN test -n "${PYTHON_VERSION}" \
    && uv python install "${PYTHON_VERSION}"

WORKDIR /app
# Ensure the image label and installed package use the same version.
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    test "$(sed -nE 's/^version = "([^"]+)"$/\1/p' pyproject.toml)" = "${SOFTWARE_VERSION}"

# Before the frozen sync
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv lock

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY ./ /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Then, use a final image without uv
FROM debian:trixie

ARG SOFTWARE_VERSION

RUN test -n "${SOFTWARE_VERSION}"

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

LABEL software="ensreg-wf"
LABEL software.version="${SOFTWARE_VERSION}"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

# Copy the Python version
COPY --from=builder --chown=${USER_NAME}:${GROUP_NAME} /python /python

# Copy the application from the builder
COPY --from=builder --chown=${USER_NAME}:${GROUP_NAME} /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["ensreg-wf", "--help"]
