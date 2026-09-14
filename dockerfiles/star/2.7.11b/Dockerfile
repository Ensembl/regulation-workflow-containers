ARG STAR_VERSION="2.7.11b"

# ----------- Builder stage -----------
FROM bitnami/minideb:bookworm AS builder

ARG STAR_VERSION

RUN install_packages  \
    build-essential \
    git \
    xxd \
    zlib1g-dev \
    ca-certificates 

## Clone STAR from GitHub, run the makefile
RUN git clone --depth 1 --branch 2.7.11b https://github.com/alexdobin/STAR.git
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
