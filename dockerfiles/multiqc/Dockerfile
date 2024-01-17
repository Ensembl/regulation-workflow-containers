FROM python:3.10-slim-buster

LABEL software="multiqc"
LABEL software.version="1.19"
LABEL about.summary="Aggregate results from bioinformatics analyses across many samples into a single report"
LABEL about.home="https://multiqc.info/"
LABEL about.documentation="https://multiqc.info/docs/"
LABEL license="https://github.com/MultiQC/MultiQC?tab=GPL-3.0-1-ov-file"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

# TODO: specify USER different that root

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh
RUN  mkdir /results

CMD ["multiqc"]