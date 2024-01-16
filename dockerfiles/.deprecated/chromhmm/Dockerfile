FROM bitnami/minideb:stretch

RUN install_packages default-jre git

WORKDIR /opt

RUN git clone https://github.com/jernst98/ChromHMM.git \
    && cd ChromHMM \
    && chmod a+rw ChromHMM.jar \
#    && rm -rf ChromHMM.zip CHROMSIZES SAMPLEDATA_HG18 edu/mit/compbio/ChromHMM ChromHMM_manual.pdf README.md \
