ARG NGMERGE_VERSION="0.3"

# ----------- Builder stage -----------
FROM bitnami/minideb:bookworm AS builder

ARG NGMERGE_VERSION

RUN install_packages \
    gcc \
    make \
    zlib1g-dev \
    git \
    ca-certificates

RUN git clone --depth 1 --branch v${NGMERGE_VERSION} https://github.com/jsh58/NGmerge.git /build/NGmerge
WORKDIR /build/NGmerge
RUN make

# ----------- Final runtime image -----------
FROM bitnami/minideb:bookworm

ARG NGMERGE_VERSION

LABEL software="NGmerge" \
      software.version="${NGMERGE_VERSION}" \
      about.summary="Merging paired-end reads and removing adapters" \
      about.home="https://github.com/jsh58/NGmerge" \
      about.documentation="https://github.com/jsh58/NGmerge/blob/master/README.md" \
      about.license="https://github.com/jsh58/NGmerge/tree/master?tab=MIT-1-ov-file"

# Runtime dependencies
RUN install_packages libgomp1

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR}  && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

# Copy built binary from builder stage
COPY --from=builder /build/NGmerge/NGmerge /usr/local/bin/

# Copy test script and set permissions
COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ${USER_NAME}
WORKDIR ${WORKDIR}
