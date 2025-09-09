ARG NGMERGE_VERSION="0.3"

# ----------- Builder stage -----------
FROM bitnami/minideb:bullseye AS builder

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
FROM bitnami/minideb:bullseye

ARG NGMERGE_VERSION

LABEL software="NGmerge" \
      software.version="${NGMERGE_VERSION}" \
      about.summary="Merging paired-end reads and removing adapters" \
      about.home="https://github.com/jsh58/NGmerge" \
      about.documentation="https://github.com/jsh58/NGmerge/blob/master/README.md" \
      about.license="https://github.com/jsh58/NGmerge/tree/master?tab=MIT-1-ov-file" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Runtime dependencies
RUN install_packages libgomp1

ENV WORKDIR="/home/ensreg/workdir"

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ensreg && \
    mkdir -p ${WORKDIR}  && \
    chown -R ensreg:ensreg /home/ensreg && \
    chmod 777 ${WORKDIR}

# Copy built binary from builder stage
COPY --from=builder /build/NGmerge/NGmerge /usr/local/bin/

# Copy test script and set permissions
COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ensreg
WORKDIR ${WORKDIR}

ENTRYPOINT ["NGmerge"]
CMD []