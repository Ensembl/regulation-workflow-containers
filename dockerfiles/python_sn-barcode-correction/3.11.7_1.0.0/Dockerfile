FROM python:3.11.7-slim-bullseye

ARG PYTHON_SN_BARCODE_CORRECTION_VERSION="3.11.7_1.0.0"

LABEL software="Python; Ensreg single cell barcode correction "
LABEL software.version="${PYTHON_SN_BARCODE_CORRECTION_VERSION}"
LABEL about.summary="Ensembl Regulation barcode correction for single-nucleus/-cell data on Python."
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

COPY barcodes_correction.py ${WORKDIR}
COPY filter_invalid_barcodes.py ${WORKDIR}

CMD ["bash"]
