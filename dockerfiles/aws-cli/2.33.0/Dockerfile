ARG AWS_CLI_VERSION="2.33.0"
ARG AWS_CLI_SHA256="db9001fd76d322a2ce9c88b5e1f306c449137541c28d04ca076f3afce366d35d"
# Only support build for amd64 platform
ARG BUILDPLATFORM=linux/amd64

FROM --platform=$BUILDPLATFORM bitnami/minideb:bookworm

ARG AWS_CLI_VERSION
ARG AWS_CLI_SHA256

LABEL software="AWS CLI"
LABEL software.version="${AWS_CLI_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="Unified tool to manage your AWS services"
LABEL about.home="https://aws.amazon.com/cli/"
LABEL about.documentation="https://docs.aws.amazon.com/cli/latest/"
LABEL about.license="https://github.com/aws/aws-cli?tab=License-1-ov-file"

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"
ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

# Install AWS CLI v2
# less and glibc are already include in the debian
RUN install_packages \
    ca-certificates \
    curl \
    unzip \
    groff

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" -o "awscliv2.zip" && \
    echo "${AWS_CLI_SHA256}  awscliv2.zip" | sha256sum -c - && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Create non-root user and working directory
RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR}

# Copy test script and set permissions
COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["aws", "help"]
