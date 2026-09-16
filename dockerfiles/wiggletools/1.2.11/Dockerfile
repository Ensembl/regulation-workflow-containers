ARG WIGGLETOOLS_VERSION="1.2.11"
ARG WIGGLETOOLS_COMMIT="d166db538ba176e2a4d748ea82a9f74a4736902c"

FROM ubuntu:22.04 AS builder

ARG WIGGLETOOLS_VERSION
ARG WIGGLETOOLS_COMMIT

RUN apt-get update \
    && apt-get install -y  --no-install-recommends\
    ca-certificates \
    git \
    gcc \
    make \
    python3 \
    libstdc++-11-dev \
    libcurl4-gnutls-dev \
    zlib1g-dev \
    libbigwig-dev \
    libhts-dev \
    libgsl-dev

RUN git init /WiggleTools \
    && cd /WiggleTools \
    && git remote add origin https://github.com/Ensembl/WiggleTools.git \
    && git fetch --depth 1 origin "${WIGGLETOOLS_COMMIT}" \
    && git checkout --detach "${WIGGLETOOLS_COMMIT}" \
    && test "$(git rev-parse HEAD)" = "${WIGGLETOOLS_COMMIT}"
WORKDIR /WiggleTools
# Upstream's `make test` harness runs under python2.7, which is not available on
# a supported Ubuntu release. The image's own run_tests.sh covers the binary.
RUN make LIBS='-lwiggletools -lBigWig -lcurl -lz -lhts -lm -lgsl -lpthread'


FROM ubuntu:22.04

ARG WIGGLETOOLS_VERSION
ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

LABEL software="WiggleTools" \
      software.version="${WIGGLETOOLS_VERSION}" \
      software.latest_version="true" \
      about.summary="Basic operations on the space of numerical functions defined on the genome using lazy evaluators for flexibility and efficiency." \
      about.home="https://github.com/Ensembl/WiggleTools" \
      about.documentation="https://github.com/Ensembl/WiggleTools/blob/master/README.md" \
      about.license="Apache-2.0"

RUN  apt-get update  \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    libbigwig0 \
    libhts3 \
    libgsl27 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /WiggleTools/bin/wiggletools /usr/local/bin/

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

ENTRYPOINT ["wiggletools"]
CMD ["--help"]
