# Standalone Python build with multistage images.

# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:0.10-python3.12-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

COPY .python-version ./

# Install Python before the project for caching
RUN uv python install  "$(cat .python-version)"

WORKDIR /app
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

LABEL software="ensreg-wf"
LABEL software.version="0.4.0"

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