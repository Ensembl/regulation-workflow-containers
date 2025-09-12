ARG WIGGLETOOLS_VERSION="1.2.11"

FROM ubuntu:20.04 AS builder

ARG WIGGLETOOLS_VERSION

RUN apt-get update \
    && apt-get install -y  --no-install-recommends\
    ca-certificates \
    git \
    gcc \
    make \
    python \
    libstdc++-10-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    libbigwig-dev \
    libhts-dev \
    libgsl-dev

RUN git clone --depth 1  --branch v1.2.11 https://github.com/Ensembl/WiggleTools.git
WORKDIR WiggleTools
RUN make LIBS='-lwiggletools -lBigWig -lcurl -lz -lhts -lm -lgsl -lpthread' \
 && make test


FROM ubuntu:20.04


ARG WIGGLETOOLS_VERSION
ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

LABEL software="WiggleTools" \
      software.version="${WIGGLETOOLS_VERSION}" \
      about.summary="Basic operations on the space of numerical functions defined on the genome using lazy evaluators for flexibility and efficiency." \
      about.home="https://github.com/Ensembl/WiggleTools" \
      about.documentation="https://github.com/Ensembl/WiggleTools/blob/master/README.md" \
      about.license="Apache-2.0" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

RUN  apt-get update  \
    && apt-get install -y --no-install-recommends \
    libbigwig0 \
    libhts3 \
    libgsl23 \
    ca-certificates

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