ARG BOWTIE2_VERSION="2.4.5"
ARG SAMTOOLS_VERSION="1.22.1"

# ----------- Builder stage -----------
FROM bitnami/minideb:bullseye AS builder

ARG BOWTIE2_VERSION
ARG SAMTOOLS_VERSION

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    unzip \
    git \
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

# Download and prepare Bowtie2
ENV BOWTIE2_BINARY_PREFIX=bowtie2-${BOWTIE2_VERSION}-linux-x86_64
RUN wget -q https://github.com/BenLangmead/bowtie2/releases/download/v${BOWTIE2_VERSION}/${BOWTIE2_BINARY_PREFIX}.zip \
    && unzip ${BOWTIE2_BINARY_PREFIX}.zip \
    && cp -r ${BOWTIE2_BINARY_PREFIX}/* /usr/local/bin/ \
    && rm -rf ${BOWTIE2_BINARY_PREFIX} ${BOWTIE2_BINARY_PREFIX}.zip

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
FROM bitnami/minideb:bullseye

ARG BOWTIE2_VERSION
ARG SAMTOOLS_VERSION

LABEL software="Bowtie2 + Samtools" \
      software.version="${BOWTIE2_VERSION}_${SAMTOOLS_VERSION}" \
      about.summary="Bowtie2: An ultrafast and memory-efficient tool for aligning sequencing reads to long reference sequences.; Samtools: Suite of programs for interacting with high-throughput sequencing data." \
      about.home="https://bowtie-bio.sourceforge.net/bowtie2/index.shtml; https://github.com/samtools/samtools" \
      about.documentation="https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml; http://www.htslib.org/doc/samtools.html" \
      about.license="Bowtie2: GPL-3.0; Samtools: MIT" \
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

# Copy built tools from builder
COPY --from=builder /usr/local/bin/samtools /usr/local/bin/
COPY --from=builder /usr/local/bin/bowtie2* /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["bowtie2"]