## Builder ##

FROM bitnami/minideb:bullseye AS builder

ENV DEBIAN_FRONTEND=noninteractive

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
RUN pip3 install --no-cache-dir git+https://github.com/CGATOxford/UMI-tools.git@master

# Clone sinto repository
RUN git clone https://github.com/timoast/sinto.git /opt/sinto

# Setting sinto directory
WORKDIR /opt/sinto

# hard reset to v 0.10.1 commit
RUN git reset --hard 37b7db1

# Install sinto using pip
RUN pip3 install .

# HTSlib installation 
ENV HTSLIB_VERSION="1.22"
ENV HTSLIB_DOWNLOAD_URL="https://github.com/samtools/htslib/releases/download/${HTSLIB_VERSION}/htslib-${HTSLIB_VERSION}.tar.bz2"

WORKDIR /tmp

RUN wget -q ${HTSLIB_DOWNLOAD_URL} \
    && tar xjvf htslib-${HTSLIB_VERSION}.tar.bz2 \
    && cd htslib-${HTSLIB_VERSION}/ \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/*

## Runtime ##

FROM bitnami/minideb:bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables and labels
ENV SINTO_VERSION="0.10.1"
ENV HTSLIB_VERSION="1.22"

LABEL software="Sinto + HTSlib"
LABEL software.version="${SINTO_VERSION}_${HTSLIB_VERSION}"
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
COPY --from=builder /usr/local/lib/python3.9/dist-packages /usr/local/lib/python3.9/dist-packages
COPY --from=builder /usr/local/bin/sinto /usr/local/bin/sinto

# Copy htslib from builder
COPY --from=builder /usr/local/bin/ /usr/local/bin


# Copy test script

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

# Default command
CMD ["bash"]

