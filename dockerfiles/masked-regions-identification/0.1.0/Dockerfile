FROM rocker/r-ver:4.3

ARG MASKED_REGIONS_IDENTIFICATION_VERSION="0.1.0"

LABEL software="Ensreg Masked Regions Identification"
LABEL software.version="${MASKED_REGIONS_IDENTIFICATION_VERSION}"
LABEL about.summary="Ensembl Regulation masked regions identification - ad hoc script."

# Runtime libraries are installed first so that purging the -dev packages below
# does not autoremove them. libc6-dev comes from the rocker base and is purged
# too: it pulls in linux-libc-dev, which accounts for every critical finding on
# this image, and the runtime only executes a pre-built R script. Compiling new
# R packages inside a running container is no longer possible as a result.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    libxml2 \
    libfontconfig1 \
    libssl3 \
    libcurl4 \
    libharfbuzz0b \
    libfribidi0 \
    libgit2-1.1 \
    libfreetype6 \
    libpng16-16 \
    libtiff5 \
    libjpeg-turbo8 \
    bedtools \
    libgomp1 \
    libgfortran5 \
    libquadmath0 \
    libblas3 \
    liblapack3 \
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
    && R -q -e 'install.packages("dplyr", Ncpus = parallel::detectCores() - 2 )' \
    && R -q -e 'install.packages("devtools", Ncpus = parallel::detectCores() - 2 )' \
    && R -q -e 'devtools::install_github("PhanstielLab/bedtoolsr")' \
    && strip /usr/local/lib/R/site-library/*/libs/*.so \
    && apt-get purge -y \
    libc6-dev \
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
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/downloaded_packages

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
