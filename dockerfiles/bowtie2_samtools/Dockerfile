FROM bitnami/minideb:stretch as builder


RUN install_packages  \
    git \
    wget \
    unzip \
    ca-certificates

ENV VERSION=2.4.5
ENV BINNARY_PREFIX=bowtie2-${VERSION}-linux-x86_64

# https://github.com/BenLangmead/bowtie2/releases/download/v2.4.5/bowtie2-2.4.5-linux-x86_64.zip
RUN wget https://github.com/BenLangmead/bowtie2/releases/download/v${VERSION}/${BINNARY_PREFIX}.zip \
    && unzip ${BINNARY_PREFIX}.zip \
    && mkdir bowtie2 \
    && cp -r ${BINNARY_PREFIX}/* bowtie2/ \
    && rm -r ${BINNARY_PREFIX} ${BINNARY_PREFIX}.zip

WORKDIR bowtie2

FROM bitnami/minideb:stretch


COPY --from=builder /bowtie2 /usr/local/bin/

RUN install_packages  \
    perl \
    python3 \
    autoconf \
    automake \
    make \
    gcc \
    musl-dev \
    bash \
    bzip2 \
    zlib1g-dev \
    libbz2-dev \
    wget \
    libcurl4-openssl-dev \
    liblzma-dev \
    libncurses-dev \
    ca-certificates

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

CMD ["bowtie2"]