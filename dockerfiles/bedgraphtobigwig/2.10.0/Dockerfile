ARG BEDGRAPHTOBIGWIG_VERSION="2.10.0"
ARG UCSC_KENT_VERSION="v479"
ARG BEDGRAPHTOBIGWIG_SHA256="22baf42aa4f01fa66a74a4d77afc6bbf5bc8354978aa2b7251a18ef9a1cc3c89"

FROM bitnami/minideb:bookworm

ARG BEDGRAPHTOBIGWIG_VERSION
ARG UCSC_KENT_VERSION
ARG BEDGRAPHTOBIGWIG_SHA256

LABEL software="bedGraphToBigWig" \
      software.version="${BEDGRAPHTOBIGWIG_VERSION}" \
      about.summary="Convert a bedGraph file to bigWig format." \
      about.home="https://hgdownload.soe.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/bigWig.html" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      coreutils \
      libkrb5-3 \
      libcurl4 \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download precompiled UCSC binary
RUN wget -O /usr/local/bin/bedGraphToBigWig \
      "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.${UCSC_KENT_VERSION}/bedGraphToBigWig" \
    && echo "${BEDGRAPHTOBIGWIG_SHA256}  /usr/local/bin/bedGraphToBigWig" | sha256sum -c - \
    && chmod +x /usr/local/bin/bedGraphToBigWig

# Create non-root user consistent with bedToBigBed and Samtools containers
ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

ENTRYPOINT ["bedGraphToBigWig"]
CMD [""]
