ARG BEDSORT_VERSION="v369"
ARG BEDSORT_SHA256="8a36530e40308aed5c3a10f2d90f96f475046a8385af1e8a4b850f61830efd63"

FROM bitnami/minideb:bookworm

ARG BEDSORT_VERSION
ARG BEDSORT_SHA256

LABEL software="bedSort" \
      software.version="${BEDSORT_VERSION}" \
      about.summary="Sort a BED file by chrom,chromStart." \
      about.home="https://hgdownload.soe.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

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

# Download UCSC binary
RUN wget -O /usr/local/bin/bedSort \
      "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.${BEDSORT_VERSION}/bedSort" \
    && echo "${BEDSORT_SHA256}  /usr/local/bin/bedSort" | sha256sum -c - \
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
