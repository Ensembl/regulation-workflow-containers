## Builder ##

ARG UMI_TOOLS_COMMIT="c457eefc5e0c47368cf3652b9b6d497b78c3050a"
ARG SINTO_COMMIT="37b7db17de64c6ddd3a8512356b966adf9ecd9a8"
ARG HTSLIB_SHA256="6250c1df297db477516e60ac8df45ed75a652d1f25b0f37f12f5b17269eafde9"

FROM bitnami/minideb:bookworm AS builder

ARG UMI_TOOLS_COMMIT
ARG SINTO_COMMIT
ARG HTSLIB_SHA256

ENV DEBIAN_FRONTEND=noninteractive
# Debian 12 marks the system Python as externally managed (PEP 668)
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Dependencies installation
RUN apt-get update && apt-get install -y \
    perl \
    python3 \
    python3-pip \
    build-essential \
    git \
    autoconf \
    automake \
    make \
    gcc \
    bash \
    wget \
    curl \
    bzip2 \
    pigz \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    libncurses-dev \
    ca-certificates && \
    apt-get clean

# Sinto installation

# Install required python libraries
RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --upgrade pip setuptools wheel

# Install umi_tools first with --no-build-isolation to bypass broken ez_setup.py
RUN pip3 install --no-cache-dir "git+https://github.com/CGATOxford/UMI-tools.git@${UMI_TOOLS_COMMIT}"

# Clone sinto repository
RUN git init /opt/sinto \
    && cd /opt/sinto \
    && git remote add origin https://github.com/timoast/sinto.git \
    && git fetch --depth 1 origin "${SINTO_COMMIT}" \
    && git checkout --detach "${SINTO_COMMIT}" \
    && test "$(git rev-parse HEAD)" = "${SINTO_COMMIT}"

# Setting sinto directory
WORKDIR /opt/sinto

# Install sinto using pip
RUN pip3 install .

# HTSlib installation 
ENV HTSLIB_VERSION="1.22"
ENV HTSLIB_DOWNLOAD_URL="https://github.com/samtools/htslib/releases/download/${HTSLIB_VERSION}/htslib-${HTSLIB_VERSION}.tar.bz2"

WORKDIR /tmp

RUN wget -q ${HTSLIB_DOWNLOAD_URL} \
    && echo "${HTSLIB_SHA256}  htslib-${HTSLIB_VERSION}.tar.bz2" | sha256sum -c - \
    && tar xjvf htslib-${HTSLIB_VERSION}.tar.bz2 \
    && cd htslib-${HTSLIB_VERSION}/ \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/*

## Runtime ##

FROM bitnami/minideb:bookworm

ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables and labels
ENV SINTO_VERSION="0.10.1"
ENV HTSLIB_VERSION="1.22"

LABEL software="Sinto + HTSlib"
LABEL software.version="${SINTO_VERSION}_${HTSLIB_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="Sinto: single-cell analysis tools;HTSlib: a C library for reading/writing high-throughput sequencing data"
LABEL about.home="https://github.com/timoast/sinto;https://github.com/samtools/htslib/"
LABEL about.documentation="https://timoast.github.io/sinto/index.html;https://www.htslib.org/doc/#manual-pages"
LABEL about.license="https://github.com/timoast/sinto?tab=MIT-1-ov-file;https://github.com/samtools/htslib/blob/develop/LICENSE"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    bash \
    perl \
    python3 \
    bzip2 \
    pigz \
    zlib1g \
    libbz2-1.0 \
    liblzma5 \
    libncurses6 \
    libcurl4 \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Create user and directories

RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

# Copy sinto from builder
COPY --from=builder /usr/local/lib/python3.11/dist-packages /usr/local/lib/python3.11/dist-packages
COPY --from=builder /usr/local/bin/sinto /usr/local/bin/sinto

# Copy htslib from builder
COPY --from=builder /usr/local/bin/ /usr/local/bin


# Copy test script

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

# Default command
CMD ["bash"]
