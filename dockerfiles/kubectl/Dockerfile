ARG KUBECTL_VERSION="1.37.0"

FROM registry.k8s.io/kubectl:v${KUBECTL_VERSION}@sha256:5ed410ebac5dc976cc717098994dcdb29bbbd38f6bd65f582311f5be4ba719cf

ARG KUBECTL_VERSION

LABEL software="kubectl"
LABEL software.version="${KUBECTL_VERSION}"
LABEL software.latest_version="true"
LABEL about.summary="Kubernetes command-line tool"
LABEL about.home="https://kubernetes.io/docs/reference/kubectl/"
LABEL about.documentation="https://kubernetes.io/docs/reference/kubectl/"
LABEL about.license="https://github.com/kubernetes/kubernetes/blob/master/LICENSE"

# The upstream image is distroless. Use its writable temporary directory for
# kubectl's cache while retaining the repository's standard non-root UID/GID.
ENV HOME="/tmp"
USER 8737:8737
WORKDIR /tmp
