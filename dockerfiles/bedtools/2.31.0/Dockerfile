FROM ubuntu:22.04

ARG BEDTOOLS_VERSION="2.31.0"
ARG BEDTOOLS_SHA256="3f9fad3cc3cf48d3471b272c0ef5525db14f00790ed938e933ce3cf6f9111623"

LABEL software="bedtools"
LABEL software.version="${BEDTOOLS_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="The swiss army knife for genome arithmetic."
LABEL about.home="https://github.com/arq5x/bedtools2"
LABEL about.documentation="https://bedtools.readthedocs.io/en/latest/"
LABEL about.license="https://github.com/arq5x/bedtools2?tab=MIT-1-ov-file"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"


RUN apt-get update  \
  && apt-get install -y --no-install-recommends  \
  wget  \
  ca-certificates \
  libkrb5-3  \
  libcurl4 \
  parallel \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O /usr/local/bin/bedtools \
      "https://github.com/arq5x/bedtools2/releases/download/v${BEDTOOLS_VERSION}/bedtools.static" \
  && echo "${BEDTOOLS_SHA256}  /usr/local/bin/bedtools" | sha256sum -c - \
  && chmod 0755 /usr/local/bin/bedtools

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ensreg -u 8737 --create-home --user-group

USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir

WORKDIR /home/ensreg/workdir

CMD [""]
