FROM ubuntu:20.04

RUN apt-get update  \
    && apt-get install -y --no-install-recommends  \
    wget  \
    libkrb5-3  \
    libcurl4 \
    parallel


RUN wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64.v369/bedSort \
    && chmod +x bedSort \
    && mv bedSort /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh \
    && mkdir /results

#ENTRYPOINT ["bedSort"]
CMD [""]