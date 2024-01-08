FROM rocker/r-ver:4.3.0

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


COPY maskedRegionsIdentification.R /usr/local/src/

COPY run_tests.sh /usr/local/bin/

RUN chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

WORKDIR /usr/local/src/

CMD ["Rscript", "maskedRegionsIdentification.R"]