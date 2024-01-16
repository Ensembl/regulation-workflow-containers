FROM ubuntu:20.04

LABEL software="bedToBigBed"
LABEL software.version="v369"
LABEL about.summary="Takes a standard bed file or a non-standard bed file with associated .as file to create a compressed bigBed version."
LABEL about.home="http://hgdownload.cse.ucsc.edu/admin/exe/"
LABEL about.documentation="https://genome.ucsc.edu/goldenPath/help/bigBed.html"
LABEL about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"


RUN apt-get update  \
    && apt-get install -y --no-install-recommends  \
    wget  \
    libkrb5-3  \
    libcurl4 \
    parallel


RUN wget --no-check-certificate https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64.v369/bedToBigBed \
    && chmod +x bedToBigBed \
    && mv bedToBigBed /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh \
    && mkdir /results \
    && mkdir /workdir

COPY bigNarrowPeak.as /workdir/


CMD [""]