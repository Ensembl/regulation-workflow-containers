ARG STAR_VERSION="2.7.11b"
ARG STAR_COMMIT="b1edc1208d91a53bf40ebae8669f71d50b994851"

# ----------- Builder stage -----------
FROM bitnami/minideb:bookworm AS builder

ARG STAR_VERSION
ARG STAR_COMMIT

RUN install_packages  \
    build-essential \
    git \
    xxd \
    zlib1g-dev \
    ca-certificates 

## Clone STAR from GitHub, run the makefile
RUN git init /STAR \
    && cd /STAR \
    && git remote add origin https://github.com/alexdobin/STAR.git \
    && git fetch --depth 1 origin "${STAR_COMMIT}" \
    && git checkout --detach "${STAR_COMMIT}" \
    && test "$(git rev-parse HEAD)" = "${STAR_COMMIT}"
WORKDIR /STAR
RUN cd source && make

# ----------- Runtime stage -----------
FROM bitnami/minideb:bookworm

RUN install_packages \
    libgomp1

## Add some metadata info
LABEL software="STAR"
LABEL software.version="2.7.11b"
LABEL software.latest_version="true"
LABEL about.home="https://github.com/alexdobin/STAR"
## Copy the binary from the builder
COPY --from=builder /STAR/source/STAR /usr/local/bin/STAR
RUN chmod +x /usr/local/bin/STAR
ENV PATH="/usr/local/bin:$PATH"

## Optional: test the build
COPY run_tests.sh /usr/local/bin/
RUN  chmod 755 /usr/local/bin/run_tests.sh

## Environment set-up
RUN useradd ensreg -u 8737 --create-home --user-group
USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir
WORKDIR /home/ensreg/workdir

## Default command
CMD ["STAR"]

# TORUN: docker build --platform=linux/amd64 -t star_2.7.11b .
