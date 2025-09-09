FROM alpine:3.12


LABEL software="Samtools"
LABEL software.version="1.15"
LABEL about.summary="Suite of programs for interacting with high-throughput sequencing data."
LABEL about.home="https://github.com/samtools/samtools"
LABEL about.documentation="http://www.htslib.org/doc/samtools.html"
LABEL about.license="https://github.com/samtools/samtools/blob/develop/LICENSE"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

RUN apk add --no-cache \
    autoconf \
    automake \
    make \
    gcc \
    musl-dev \
    perl \
    bash \
    zlib-dev \
    bzip2-dev \
    xz-dev \
    curl-dev \
    libressl-dev \
    ncurses-dev \
    jq

ENV SAMTOOLS_VERSION="1.15.1"
ENV SAMTOOLS_DOWNLOAD_URL="https://github.com/samtools/samtools/releases/download/${SAMTOOLS_VERSION}/samtools-${SAMTOOLS_VERSION}.tar.bz2"

WORKDIR /tmp

RUN wget -q ${SAMTOOLS_DOWNLOAD_URL} \
    && tar xjvf samtools-${SAMTOOLS_VERSION}.tar.bz2 \
    && cd samtools-${SAMTOOLS_VERSION}/ \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/*

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

CMD ["samtools"]
