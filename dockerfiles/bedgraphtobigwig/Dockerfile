FROM ubuntu:20.04

LABEL software="bedGraphToBigWig"
LABEL software.version="2.10.0"
LABEL about.summary="Convert a bedGraph file to bigWig format."
LABEL about.home="http://hgdownload.cse.ucsc.edu/admin/exe/"
LABEL about.documentation="https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/"
LABEL about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"


RUN apt-get update  \
    && apt-get install -y --no-install-recommends  \
    wget  \
    libkrb5-3  \
    libcurl4


RUN wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/bedGraphToBigWig \
    && chmod +x bedGraphToBigWig \
    && mv bedGraphToBigWig /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

ENTRYPOINT ["bedGraphToBigWig"]
CMD [""]
