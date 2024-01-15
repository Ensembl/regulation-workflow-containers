FROM bitnami/minideb:bullseye as builder

RUN install_packages  \
    gcc \
    make \
    zlib1g-dev \
    git \
    ca-certificates

RUN git clone --depth 1 --branch v0.6.1 https://github.com/jsh58/Genrich.git
WORKDIR Genrich
RUN make

FROM bitnami/minideb:bullseye

LABEL software="Genrich"
LABEL software.version="0.6.1"
LABEL about.summary="Detecting sites of genomic enrichment"
LABEL about.home="https://github.com/jsh58/Genrich"
LABEL about.documentation="https://github.com/jsh58/Genrich/blob/v0.6.1/README.md"
LABEL about.license="https://github.com/jsh58/Genrich#MIT-1-ov-file"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

COPY --from=builder /Genrich/Genrich /usr/local/bin/
WORKDIR /mnt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

COPY mt.queryname_sorted.bam /mnt/

CMD ["Genrich"]