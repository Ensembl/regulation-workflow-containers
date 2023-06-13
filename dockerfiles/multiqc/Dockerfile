FROM python:3.10-slim-buster


LABEL base.image="ensembl-multiqc:latest"
LABEL version="0.1"
LABEL software="multiqc"
LABEL software.version="1.13"
LABEL about.summary="MultiQC: summarize analysis results for multiple tools and samples in a single report"
LABEL about.home="https://multiqc.info/"
LABEL about.documentation="https://multiqc.info/docs/#custom-content"
LABEL license="https://github.com/ewels/MultiQC/blob/696cb1b8f5c2eec2258ac608098e5658cafefec0/LICENSE"
LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

# TODO: specify USER different that root

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh
RUN  mkdir /results

CMD ["multiqc"]