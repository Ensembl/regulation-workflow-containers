ARG BEDTOBIGBED_VERSION="2.10.0"
ARG UCSC_KENT_VERSION="v479"
ARG BEDTOBIGBED_SHA256="aa42073701d102b7eb5f7e6fe3c8f8057e5f983fb9967a9e501f044eb14c99f0"

FROM bitnami/minideb:bookworm

ARG BEDTOBIGBED_VERSION
ARG UCSC_KENT_VERSION
ARG BEDTOBIGBED_SHA256

LABEL software="bedToBigBed" \
      software.version="${BEDTOBIGBED_VERSION}" \
      software.latest_version="true" \
      about.summary="Convert BED file to bigBed format." \
      about.home="https://hgdownload.soe.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/bigBed.html" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"


# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      coreutils \
      libkrb5-3 \
      libcurl4 \
      parallel \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download precompiled UCSC binary
RUN wget -O /usr/local/bin/bedToBigBed \
      "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.${UCSC_KENT_VERSION}/bedToBigBed" \
    && echo "${BEDTOBIGBED_SHA256}  /usr/local/bin/bedToBigBed" | sha256sum -c - \
    && chmod +x /usr/local/bin/bedToBigBed


RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
COPY --chown=${USER_NAME}:${GROUP_NAME} bigNarrowPeak.as ${WORKDIR}/

RUN chmod 755 /usr/local/bin/run_tests.sh

CMD ["bedToBigBed"]
