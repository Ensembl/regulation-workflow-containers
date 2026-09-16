ARG PYTHON_VERSION="3.10"

# ----------- Builder stage -----------
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

# MOODS-python ships no wheel, so it is compiled here and only the installed
# files are copied into the runtime image, which keeps the compiler out of it.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --prefix=/install -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt

# ----------- Final runtime image -----------
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG MOODS_VERSION="1.9.4.1"
ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

LABEL software="MOODS" \
      software.version="${MOODS_VERSION}" \
      software.latest_version="true" \
      about.summary="Motif Occurrence Detection Suite" \
      about.home="https://github.com/jhkorhonen/MOODS" \
      about.documentation="https://github.com/jhkorhonen/MOODS/blob/master/readme.MD" \
      about.license="GPL-3.0"

# Environment variables for user and workdir
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Create non-root user and directories
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

ENTRYPOINT ["moods-dna.py"]
CMD [""]
