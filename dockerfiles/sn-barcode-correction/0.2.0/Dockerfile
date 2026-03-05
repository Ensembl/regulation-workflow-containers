FROM python:3.11.7-slim-bullseye

ARG BARCODE_CORRECTION_VERSION="0.2.0"

LABEL software="Ensreg single nucleus barcode correction "
LABEL software.version="${BARCODE_CORRECTION_VERSION}"
LABEL about.summary="Ensembl Regulation barcode correction for single-nucleus/-cell data on Python."

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR}  && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

COPY barcodes_correction.py ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["python"]
