FROM bitnami/minideb:bullseye as builder

RUN install_packages  \
    gcc \
    make \
    zlib1g-dev \
    git \
    ca-certificates

RUN git clone --depth 1 --branch v0.3 https://github.com/jsh58/NGmerge.git
WORKDIR NGmerge
RUN make

FROM bitnami/minideb:bullseye

LABEL software="NGmerge"
LABEL software.version="0.3.0"
LABEL about.summary="Merging paired-end reads and removing adapters"
LABEL about.home="https://github.com/jsh58/NGmerge"
LABEL about.documentation="https://github.com/jsh58/NGmerge/blob/master/README.md"
LABEL about.license="https://github.com/jsh58/NGmerge/tree/master?tab=MIT-1-ov-file"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

RUN install_packages  \
    libgomp1


COPY --from=builder /NGmerge/NGmerge /usr/local/bin/
WORKDIR /mnt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

CMD ["NGmerge"]