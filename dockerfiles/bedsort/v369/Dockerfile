ARG BEDSORT_VERSION="v369"

FROM bitnami/minideb:bullseye

ARG BEDSORT_VERSION

LABEL software="bedSort" \
      software.version="${BEDSORT_VERSION}" \
      about.summary="Sort a BED file by chrom,chromStart." \
      about.home="http://hgdownload.cse.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      libkrb5-3 \
      libcurl4 \
      parallel \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download UCSC binary
RUN wget --no-check-certificate -O /usr/local/bin/bedSort \
      https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64.${BEDSORT_VERSION}/bedSort \
    && chmod +x /usr/local/bin/bedSort

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

CMD [""]