FROM ubuntu:20.04

ARG FASTP_VERSION="0.23.2"

LABEL software="fastp" \
      software.version="${FASTP_VERSION}" \
      about.summary="An ultra-fast all-in-one FASTQ preprocessor (QC/adapters/trimming/filtering/splitting/merging...)" \
      about.home="https://github.com/OpenGene/fastp" \
      about.documentation="https://github.com/OpenGene/fastp/blob/master/README.md" \
      about.license="https://github.com/OpenGene/fastp?tab=MIT-1-ov-file"

ENV PREBUILT_BINARY="http://opengene.org/fastp/fastp.${FASTP_VERSION}" \
    WORKDIR="/home/ensreg/workdir"

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -u 8737 -m -s /bin/bash ensreg && \
    mkdir -p ${WORKDIR} && \
    chown -R ensreg:ensreg /home/ensreg && \
    chmod 777 ${WORKDIR}

RUN wget --no-check-certificate ${PREBUILT_BINARY} -O /usr/local/bin/fastp && \
    chmod +x /usr/local/bin/fastp

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ensreg
WORKDIR ${WORKDIR}

CMD ["fastp"]