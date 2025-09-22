FROM python:3.11.7-slim-bullseye

LABEL software="python"
LABEL software.version="3.11.7"
LABEL about.summary="Python is a programming language that lets you work quickly and integrate systems more effectively."
LABEL about.home="https://www.python.org/"
LABEL about.documentation="https://docs.python.org/3/"
LABEL about.license="https://docs.python.org/3/license.html#psf-license"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

USER 8737

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

WORKDIR ${WORKDIR}

CMD ["python"]
