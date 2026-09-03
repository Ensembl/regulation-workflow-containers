ARG SAMTOOLS_VERSION="1.22.1"

# ----------- Builder stage -----------
FROM bitnami/minideb:bookworm AS builder

ARG SAMTOOLS_VERSION

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    ca-certificates \
    libbz2-dev \
    liblzma-dev \
    libncurses-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    autoconf \
    automake \
    python3 \
    perl \
    && rm -rf /var/lib/apt/lists/*

# Download, build, and install Samtools
ENV SAMTOOLS_DOWNLOAD_URL="https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2"
WORKDIR /tmp
RUN wget -q ${SAMTOOLS_DOWNLOAD_URL} \
    && tar -xjf samtools-${SAMTOOLS_VERSION}.tar.bz2 \
    && cd samtools-${SAMTOOLS_VERSION} \
    && ./configure --prefix=/usr/local \
    && make \
    && make install \
    && cd /tmp \
    && rm -rf samtools-${SAMTOOLS_VERSION} samtools-${SAMTOOLS_VERSION}.tar.bz2

# ----------- Final runtime image -----------
FROM bitnami/minideb:bookworm

ARG SAMTOOLS_VERSION

LABEL software="Samtools" \
      software.version="${SAMTOOLS_VERSION}" \
      about.summary="Samtools: Suite of programs for interacting with high-throughput sequencing data." \
      about.home="https://github.com/samtools/samtools" \
      about.documentation="http://www.htslib.org/doc/samtools.html" \
      about.license="MIT" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    bash \
    perl \
    python3 \
    bzip2 \
    zlib1g \
    libbz2-1.0 \
    liblzma5 \
    libncurses6 \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR}  && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

# Copy Samtools binary from builder
COPY --from=builder /usr/local/bin/samtools /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

# Default command
CMD ["samtools"]
