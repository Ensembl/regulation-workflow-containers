ARG BEDGRAPHTOBIGWIG_VERSION="2.10.0"

FROM bitnami/minideb:bookworm

ARG BEDGRAPHTOBIGWIG_VERSION

LABEL software="bedGraphToBigWig" \
      software.version="${BEDGRAPHTOBIGWIG_VERSION}" \
      about.summary="Convert a bedGraph file to bigWig format." \
      about.home="http://hgdownload.cse.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/bigWig.html" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      libkrb5-3 \
      libcurl4 \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download precompiled UCSC binary
RUN wget --no-check-certificate -O /usr/local/bin/bedGraphToBigWig \
      https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64.v479/bedGraphToBigWig \
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
