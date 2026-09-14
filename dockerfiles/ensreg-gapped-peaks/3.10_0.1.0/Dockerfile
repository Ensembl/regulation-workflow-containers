ARG PYTHON_VERSION="3.10"

# ----------- Builder stage -----------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# Compilers and headers stay in this stage: shipping them in the runtime image
# pulls in linux-libc-dev and full perl, which dominate its CVE count.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    gcc \
    g++ \
    make \
    libz-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt

# ----------- Final runtime image -----------
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG PYTHON_WF_HELPER_VERSION="3.10_0.1.0"

LABEL software="Ensreg Gapped Peaks generation"
LABEL software.version="${PYTHON_WF_HELPER_VERSION}"
LABEL about.summary="Ensembl Regulation Gapped Peaks generation - ad hoc script."

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# pybedtools shells out to bedtools, so it is a runtime dependency.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    bedtools \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

RUN mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY writeGappedPeaks.py ${WORKDIR}/

CMD ["python"]
