FROM python:3.11.7-slim-bullseye

ARG BARCODE_PREPROCESSING_VERSION="0.1.0"

LABEL software="Ensreg single nucleus barcode trimming "
LABEL software.version="${BARCODE_PREPROCESSING_VERSION}"
LABEL about.summary="Ensembl Regulation barcode trimming for single-nucleus/-cell data on Python."

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Install pigz
RUN apt-get update && \
    apt-get install -y --no-install-recommends pigz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR}  && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

COPY sn_atac_barcodes_preprocessing.py ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["python"]
