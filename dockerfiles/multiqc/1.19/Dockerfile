FROM python:3.11-slim-bookworm

LABEL software="multiqc"
LABEL software.version="1.19"
LABEL about.summary="Aggregate results from bioinformatics analyses across many samples into a single report"
LABEL about.home="https://multiqc.info/"
LABEL about.documentation="https://multiqc.info/docs/"
LABEL license="https://github.com/MultiQC/MultiQC?tab=GPL-3.0-1-ov-file"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"


COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ensreg -u 8737 --create-home --user-group

USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir

WORKDIR /home/ensreg/workdir


CMD ["multiqc"]