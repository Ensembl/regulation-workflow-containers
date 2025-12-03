FROM python:3.11.7-slim-bullseye

ARG BARCODE_UPDATE="0.1.0"

LABEL software="Ensreg snFASTQ files cleanup and filtering after barcodes correction"
LABEL software.version="${BARCODE_UPDATE}"
LABEL about.summary="Ensembl Regulation single-nucleus FASTQ files cleanup and filtering after barcodes correction based on whitelist matching on Python."

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY sn_fastq_filtering_update.py ${WORKDIR}

CMD ["python"]
