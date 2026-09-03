# Declare once, visible to all stages
ARG FASTQC_VERSION=0.11.9
ARG FASTQC_URL="https://www.bioinformatics.babraham.ac.uk/projects/fastqc"

# ----------- Builder stage -----------
FROM alpine:3.22 AS builder

ARG FASTQC_VERSION
ARG FASTQC_URL

ENV ZIP_FILE="fastqc_v${FASTQC_VERSION}.zip"

RUN apk add --no-cache wget unzip \
 && wget ${FASTQC_URL}/${ZIP_FILE} -O /${ZIP_FILE} \
 && unzip /${ZIP_FILE} -d /opt \
 && rm /${ZIP_FILE}

# ----------- Final runtime image -----------
FROM alpine:3.22

ARG FASTQC_VERSION

LABEL software="FastQC" \
      software.version="${FASTQC_VERSION}" \
      about.summary="A quality control tool for high throughput sequence data." \
      about.home="http://www.bioinformatics.babraham.ac.uk/projects/fastqc/" \
      about.documentation="http://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/" \
      license="https://www.gnu.org/licenses/gpl-3.0.html" \
      maintainer="David Urbina-Gómez <durbina@ebi.ac.uk>"

# Promote ARG into ENV so it persists in containers
ENV DESTINATION="/opt" \
    FASTQC_VERSION=${FASTQC_VERSION} \
    JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"

# Pick up Alpine security updates released after the base image was published
RUN apk -U upgrade --no-cache

RUN apk add --no-cache \
      perl \
      openjdk11 \
      fontconfig \
      ttf-dejavu

COPY --from=builder /opt/FastQC ${DESTINATION}/FastQC

RUN chmod 755 ${DESTINATION}/FastQC/fastqc \
 && ln -s ${DESTINATION}/FastQC/fastqc /usr/local/bin/fastqc

RUN addgroup -g 8737 ensreg \
 && adduser -D -u 8737 -G ensreg ensreg \
 && mkdir -p /home/ensreg/workdir \
 && chown -R ensreg:ensreg /home/ensreg /opt/FastQC

COPY run_tests.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/run_tests.sh

USER ensreg
WORKDIR /home/ensreg/workdir

CMD ["fastqc", "--help"]