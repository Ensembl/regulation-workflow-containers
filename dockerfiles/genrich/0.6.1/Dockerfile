FROM bitnami/minideb:bookworm as builder

RUN install_packages  \
    gcc \
    make \
    zlib1g-dev \
    git \
    ca-certificates

RUN git clone --depth 1 --branch v0.6.1 https://github.com/jsh58/Genrich.git
WORKDIR Genrich
RUN make

FROM bitnami/minideb:bookworm

LABEL software="Genrich"
LABEL software.version="0.6.1"
LABEL software.latest_version="true"
LABEL about.summary="Detecting sites of genomic enrichment"
LABEL about.home="https://github.com/jsh58/Genrich"
LABEL about.documentation="https://github.com/jsh58/Genrich/blob/v0.6.1/README.md"
LABEL about.license="https://github.com/jsh58/Genrich#MIT-1-ov-file"

COPY --from=builder /Genrich/Genrich /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ensreg -u 8737 --create-home --user-group

USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir

COPY mt.queryname_sorted.bam /home/ensreg/workdir

WORKDIR /home/ensreg/workdir

CMD ["Genrich"]
