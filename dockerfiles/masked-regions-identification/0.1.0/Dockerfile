FROM rocker/r-ver:4.3.0

ARG MASKED_REGIONS_IDENTIFICATION_VERSION="0.1.0"

LABEL software="Ensreg Masked Regions Identification"
LABEL software.version="${MASKED_REGIONS_IDENTIFICATION_VERSION}"
LABEL about.summary="Ensembl Regulation masked regions identification - ad hoc script."

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libxml2-dev \
    libfontconfig1-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libgit2-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    bedtools \
    && rm -rf /tmp/downloaded_packages \
    && R -q -e 'install.packages("dplyr", Ncpus = parallel::detectCores() - 2 )' \
    && R -q -e 'install.packages("devtools", Ncpus = parallel::detectCores() - 2 )' \
    && R -q -e 'devtools::install_github("PhanstielLab/bedtoolsr")' \
    && strip /usr/local/lib/R/site-library/*/libs/*.so

ARG USER_NAME="ensreg"
ARG GROUP_NAME="ensreg"

ENV HOME="/home/${USER_NAME}"
ENV WORKDIR="${HOME}/workdir"

RUN useradd ${USER_NAME} -u 8737 --create-home --user-group

COPY run_tests.sh /usr/local/bin/

RUN chmod 755 /usr/local/bin/run_tests.sh \
    && mkdir ${WORKDIR} \
    && chmod 777 ${WORKDIR}

COPY maskedRegionsIdentification.R ${WORKDIR}

USER ${USER_NAME}
WORKDIR ${WORKDIR}

CMD ["Rscript", "maskedRegionsIdentification.R"]