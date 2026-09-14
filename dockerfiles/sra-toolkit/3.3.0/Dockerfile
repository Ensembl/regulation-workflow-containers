FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables and labels
ENV SRA_TOOLKIT_VERSION="3.3.0"
ENV SRA_TOOLKIT_DOWNLOAD_URL="https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/3.3.0/sratoolkit.${SRA_TOOLKIT_VERSION}-ubuntu64.tar.gz"

LABEL software="SRA Toolkit"
LABEL software.version="${SRA_TOOLKIT_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="The SRA Toolkit and SDK from NCBI is a collection of tools and libraries for using data in the INSDC Sequence Read Archives"
LABEL about.home="https://github.com/ncbi/sra-tools/"
LABEL about.documentation="https://github.com/ncbi/sra-tools/wiki"
LABEL about.license="https://github.com/ncbi/sra-tools?tab=License-1-ov-file#readme"

# Dependencies installation
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    zlib1g \
    libncurses6 \
    libstdc++6 && \
    apt-get clean

WORKDIR /tmp

RUN wget ${SRA_TOOLKIT_DOWNLOAD_URL} \
    && tar -xzf sratoolkit.${SRA_TOOLKIT_VERSION}-ubuntu64.tar.gz \
    && mv sratoolkit.${SRA_TOOLKIT_VERSION}-ubuntu64 /opt/sratoolkit \
    && rm sratoolkit.${SRA_TOOLKIT_VERSION}-ubuntu64.tar.gz


ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"
ENV PATH="/opt/sratoolkit/bin:${PATH}"

RUN useradd -u 8737 -m -s /bin/bash ${USER_NAME} && \
    mkdir -p ${WORKDIR} /results && \
    chown -R ${USER_NAME}:${GROUP_NAME} ${HOME} && \
    chmod 777 ${WORKDIR} /results

USER ${USER_NAME}
WORKDIR ${WORKDIR}

# Config cache for prefetch
RUN mkdir -p $HOME/.ncbi $HOME/cache
RUN chown -R ${USER_NAME}:${GROUP_NAME} $HOME/cache

RUN vdb-config --set /repository/user/cache-enabled=true
RUN vdb-config --set /repository/user/main/public/root=$HOME/cache

# Copy test script
COPY --chown=${USER_NAME}:${GROUP_NAME} run_tests.sh /usr/local/bin/run_tests.sh
RUN chmod 755 /usr/local/bin/run_tests.sh

# Default command
CMD ["bash"]
