ARG BEDTOBIGBED_VERSION="2.10.0"

FROM bitnami/minideb:bullseye

ARG BEDTOBIGBED_VERSION

LABEL software="bedToBigBed" \
      software.version="${BEDTOBIGBED_VERSION}" \
      about.summary="Convert BED file to bigBed format." \
      about.home="http://hgdownload.cse.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/bigBed.html" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"


# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      libkrb5-3 \
      libcurl4 \
      parallel \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download precompiled UCSC binary
RUN wget --no-check-certificate -O /usr/local/bin/bedToBigBed \
      https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed \
    && chmod +x /usr/local/bin/bedToBigBed


RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}


# Copy scripts and resources
COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
COPY --chown=${USER_NAME}:${GROUP_NAME} bigNarrowPeak.as ${WORKDIR}/

RUN chmod 755 /usr/local/bin/run_tests.sh

CMD ["bedToBigBed"]