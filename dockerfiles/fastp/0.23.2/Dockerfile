ARG FASTP_VERSION="0.23.2"
ARG FASTP_SOURCE_SHA256="185bd58732e57474fa08aae90e154fbc05f3e437ee2b434386dd2266d60d8ef6"

FROM ubuntu:22.04 AS builder

ARG FASTP_VERSION
ARG FASTP_SOURCE_SHA256

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      libdeflate-dev \
      libisal-dev \
      wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

RUN wget -O fastp.tar.gz \
      "https://github.com/OpenGene/fastp/archive/refs/tags/v${FASTP_VERSION}.tar.gz" && \
    echo "${FASTP_SOURCE_SHA256}  fastp.tar.gz" | sha256sum -c - && \
    tar -xzf fastp.tar.gz && \
    make -C "fastp-${FASTP_VERSION}" -j"$(nproc)" && \
    install -m 0755 "fastp-${FASTP_VERSION}/fastp" /usr/local/bin/fastp

FROM ubuntu:22.04

ARG FASTP_VERSION

LABEL software="fastp" \
      software.version="${FASTP_VERSION}" \
      about.summary="An ultra-fast all-in-one FASTQ preprocessor (QC/adapters/trimming/filtering/splitting/merging...)" \
      about.home="https://github.com/OpenGene/fastp" \
      about.documentation="https://github.com/OpenGene/fastp/blob/master/README.md" \
      about.license="https://github.com/OpenGene/fastp?tab=MIT-1-ov-file"

ENV WORKDIR="/home/ensreg/workdir"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libdeflate0 \
      libisal2 \
      libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -u 8737 -m -s /bin/bash ensreg && \
    mkdir -p ${WORKDIR} && \
    chown -R ensreg:ensreg /home/ensreg && \
    chmod 777 ${WORKDIR}

COPY --from=builder /usr/local/bin/fastp /usr/local/bin/fastp

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ensreg
WORKDIR ${WORKDIR}

CMD ["fastp"]
