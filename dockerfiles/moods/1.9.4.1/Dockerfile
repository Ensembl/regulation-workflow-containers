FROM python:3.10.7-bullseye

ARG MOODS_VERSION="1.9.4.1"
ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

LABEL software="MOODS" \
      software.version="${MOODS_VERSION}" \
      about.summary="Motif Occurrence Detection Suite" \
      about.home="https://github.com/jhkorhonen/MOODS" \
      about.documentation="https://github.com/jhkorhonen/MOODS/blob/master/readme.MD" \
      about.license="GPL-3.0" \
      maintainer="David Urbina-Gómez" \
      maintainer.email="durbina@ebi.ac.uk"

# Environment variables for user and workdir
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Create non-root user and directories
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

USER ${USER_NAME}
WORKDIR ${WORKDIR}

COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

ENTRYPOINT ["moods-dna.py"]
CMD [""]