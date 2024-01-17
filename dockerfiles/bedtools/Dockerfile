FROM ubuntu:20.04

LABEL software="bedtools"
LABEL software.version="2.31.0"
LABEL about.summary="The swiss army knife for genome arithmetic."
LABEL about.home="https://github.com/arq5x/bedtools2"
LABEL about.documentation="https://bedtools.readthedocs.io/en/latest/"
LABEL about.license="https://github.com/arq5x/bedtools2?tab=MIT-1-ov-file"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"


RUN apt-get update  \
  && apt-get install -y --no-install-recommends  \
  wget  \
  libkrb5-3  \
  libcurl4 \
  parallel


RUN wget --no-check-certificate https://github.com/arq5x/bedtools2/releases/download/v2.31.0/bedtools.static \
  && mv bedtools.static bedtools \
  && chmod a+x bedtools \
  && mv bedtools /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

CMD [""]

