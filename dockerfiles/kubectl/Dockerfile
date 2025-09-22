FROM bitnami/kubectl:1.23

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Create user, group, and working directory
RUN groupadd -g 8737 ${GROUP_NAME} && \
    useradd -u 8737 -m -s /bin/bash -g ${GROUP_NAME} ${USER_NAME} && \
    mkdir -p ${WORKDIR} \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["kubectl"]