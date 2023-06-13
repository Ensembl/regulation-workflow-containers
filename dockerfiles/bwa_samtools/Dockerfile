FROM alpine:3.12 AS bwa_builder

RUN apk add --no-cache \
    gcc \
    make \
    libc-dev \
    zlib-dev

ENV BWA_VERSION="0.7.17"
ENV BWA_DOWNLOAD_URL="https://github.com/lh3/bwa/releases/download/v${BWA_VERSION}/bwa-${BWA_VERSION}.tar.bz2"

WORKDIR /tmp

RUN wget -q ${BWA_DOWNLOAD_URL} \
    && tar xjvf bwa-${BWA_VERSION}.tar.bz2 \
    && cd /tmp/bwa-${BWA_VERSION} \
    && make \
    && cp -r /tmp/bwa-${BWA_VERSION}/bwa /usr/local/bin \
    && rm -rf /tmp/*

FROM  alpine:3.12

#LABEL base.image="ensembl-bwa:latest"
#LABEL version="0.1"
#LABEL software="bwa"
#LABEL software.version="0.7.17"
#LABEL about.summary="BWA is a software package for mapping low-divergent sequences against a large reference genome."
#LABEL about.home="http://bio-bwa.sourceforge.net/"
#LABEL about.documentation="http://bio-bwa.sourceforge.net/bwa.shtml"
#LABEL license="http://bio-bwa.sourceforge.net/bwa.shtml#13"

#LABEL base.image="ensembl-samtools:latest"
#LABEL version="0.1"
#LABEL software="Samtools"
#LABEL software.version="1.11"
#LABEL about.summary="Samtools is a suite of programs for interacting with high-throughput sequencing data."
#LABEL about.home="https://github.com/samtools/samtools"
#LABEL about.documentation="http://www.htslib.org/doc/samtools.html"
#LABEL license="https://github.com/samtools/samtools/blob/develop/LICENSE"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

COPY --from=bwa_builder /usr/local/bin/* /usr/local/bin/

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
    ncurses-dev

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

CMD ["bwa"]

