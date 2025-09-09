FROM python:3.10.7-bullseye

LABEL software="MOODS"
LABEL software.version="1.9.4.1"
LABEL about.summary="Motif Occurrence Detection Suite"
LABEL about.home="https://github.com/jhkorhonen/MOODS"
LABEL about.documentation="https://github.com/jhkorhonen/MOODS/blob/master/readme.MD"
LABEL about.license="https://github.com/jhkorhonen/MOODS?tab=GPL-3.0-2-ov-file"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

ENTRYPOINT ["moods-dna.py"]
CMD [""]
