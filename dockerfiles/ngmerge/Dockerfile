FROM bitnami/minideb:stretch as builder

RUN install_packages  \
    gcc \
    make \
    zlib1g-dev \
    git \
    ca-certificates

RUN git clone --depth 1 --branch v0.3 https://github.com/jsh58/NGmerge.git
WORKDIR NGmerge
RUN make

FROM bitnami/minideb:stretch

RUN install_packages  \
    libgomp1


COPY --from=builder /NGmerge/NGmerge /usr/local/bin/
WORKDIR /mnt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

#COPY mt.queryname_sorted.bam /mnt/

CMD ["NGmerge"]