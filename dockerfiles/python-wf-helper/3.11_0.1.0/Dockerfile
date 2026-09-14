FROM python:3.11-slim-bookworm


ARG PYTHON_WF_HELPER_VERSION="3.11_0.1.0"

LABEL software="Python Ensreg Workflow Helper"
LABEL software.version="${PYTHON_WF_HELPER_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="Python Ensembl Regulation workflows helper."
LABEL about.license="https://docs.python.org/3/license.html#psf-license"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["python"]
