FROM python:3.11-slim-bookworm


ARG BARCODE_UPDATE="0.5.1"

LABEL software="Ensreg snFASTQ files cleanup and filtering after barcodes correction"
LABEL software.version="${BARCODE_UPDATE}"
LABEL software.latest_version="true"
LABEL about.summary="Ensembl Regulation single-nucleus FASTQ files cleanup and filtering after barcodes correction based on whitelist matching on Python."

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Install pigz
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
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

COPY sn_fastq_filtering_update.py ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["python"]
