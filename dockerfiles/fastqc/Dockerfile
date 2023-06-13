FROM alpine:3.12 AS builder

USER root

ENV FASTQC_URL="https://www.bioinformatics.babraham.ac.uk/projects/fastqc"

ENV FASTQC_VERSION="0.11.9"
ENV ZIP_FILE="fastqc_v${FASTQC_VERSION}.zip"

RUN apk add --no-cache \
    wget \
    unzip

RUN wget ${FASTQC_URL}/${ZIP_FILE} -O /${ZIP_FILE} \
  && unzip - /${ZIP_FILE} -d / \
  && rm /${ZIP_FILE}

FROM alpine:3.12

LABEL base.image="ensembl-fastqc:latest"
LABEL version="0.1"
LABEL software="FastQC"
LABEL software.version="0.11.9"
LABEL about.summary="A quality control tool for high throughput sequence data."
LABEL about.home="http://www.bioinformatics.babraham.ac.uk/projects/fastqc/"
LABEL about.documentation="http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/"
LABEL license="https://www.gnu.org/licenses/gpl-3.0.html"
LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

# TODO: specify USER different that root

ENV DESTINATION="/opt"
COPY --from=builder /FastQC ${DESTINATION}/FastQC

RUN apk add --no-cache \
    perl \
    openjdk11 \
    fontconfig \
    ttf-dejavu

RUN chmod 755 ${DESTINATION}/FastQC/fastqc \
  && ln -s ${DESTINATION}/FastQC/fastqc /usr/local/bin/fastqc

COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

CMD ["fastqc"]
