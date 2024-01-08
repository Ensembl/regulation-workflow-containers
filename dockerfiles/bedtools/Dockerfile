FROM ubuntu:20.04

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

