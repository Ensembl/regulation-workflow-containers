FROM python:3.10.12-slim-bullseye

ARG PYTHON_WF_HELPER_VERSION="3.10.12_0.1.0"

LABEL software="Ensreg Gapped Peaks generation"
LABEL software.version="${PYTHON_WF_HELPER_VERSION}"
LABEL about.summary="Ensembl Regulation Gapped Peaks generation - ad hoc script."

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    gcc \
    g++ \
    make \
    libz-dev \
    bedtools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt


COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY writeGappedPeaks.py ${WORKDIR}/

CMD ["python"]


