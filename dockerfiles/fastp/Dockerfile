FROM ubuntu:20.04

USER root
# TODO: specify USER different that root

ENV FASTP_VERSION="0.23.2"
ENV PREBUILT_BINARY="http://opengene.org/fastp/fastp.${FASTP_VERSION}"

RUN apt-get update  \
    && apt-get install -y --no-install-recommends  \
    wget

RUN wget --no-check-certificate ${PREBUILT_BINARY} \
    && mv "fastp.${FASTP_VERSION}" /usr/local/bin/fastp \
    && chmod a+x /usr/local/bin/fastp

COPY run_tests.sh /usr/local/bin/

RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

CMD ["fastp"]


