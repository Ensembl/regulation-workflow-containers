ARG FASIZE_VERSION="v479"
ARG FASIZE_SHA256="d9072e9c630d82739571b81f47790058e4e5e7809166cd84ee2a30d6369ddb60"
ARG FASIZE_PLATFORM="linux/amd64"

FROM --platform=${FASIZE_PLATFORM} bitnami/minideb:bookworm

ARG FASIZE_VERSION
ARG FASIZE_SHA256

LABEL software="faSize" \
      software.version="${FASIZE_VERSION}" \
      software.latest_version="true" \
      about.summary="Print total base count in fa files." \
      about.home="https://hgdownload.soe.ucsc.edu/admin/exe/" \
      about.documentation="https://genome.ucsc.edu/goldenPath/help/" \
      about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      wget \
      coreutils \
      libkrb5-3 \
      libcurl4 \
      ca-certificates \
      bash \
    && rm -rf /var/lib/apt/lists/*

# Download and verify the versioned UCSC binary before making it executable
RUN wget -O /usr/local/bin/faSize \
      "https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.${FASIZE_VERSION}/faSize" \
    && echo "${FASIZE_SHA256}  /usr/local/bin/faSize" | sha256sum -c - \
    && chmod 0755 /usr/local/bin/faSize

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

ENTRYPOINT ["faSize"]
CMD ["--help"]
