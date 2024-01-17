FROM ubuntu:20.04

LABEL software="faSize"
LABEL software.version="v459"
LABEL about.summary="Print total base count in fa files."
LABEL about.home="http://hgdownload.cse.ucsc.edu/admin/exe/"
LABEL about.documentation="https://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/"
LABEL about.license="https://github.com/ucscGenomeBrowser/kent/blob/master/LICENSE"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"


RUN apt-get update  \
    && apt-get install -y --no-install-recommends  \
    wget  \
    libkrb5-3  \
    libcurl4


RUN wget http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/faSize \
    && chmod +x faSize \
    && mv faSize /usr/local/bin/

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh \
    && mkdir /results

ENTRYPOINT ["faSize"]
CMD [""]
