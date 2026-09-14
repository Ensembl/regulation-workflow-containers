FROM bash:5.2

LABEL software="Bash"
LABEL software.version="5.2"
LABEL about.summary="GNU Project's Bourne Again SHell"
LABEL about.home="https://tiswww.case.edu/php/chet/bash/bashtop.html"
LABEL about.documentation="https://tiswww.case.edu/php/chet/bash/README"
LABEL about.license="https://www.gnu.org/licenses/gpl-3.0.html"

# Alpine base images are rebuilt only on point releases, so pick up updates here
RUN apk -U upgrade --no-cache

RUN apk add --no-cache tar pigz jq curl

RUN addgroup -g 8737 ensreg \
    && adduser -u 8737 -G ensreg -D ensreg

USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir

WORKDIR /home/ensreg/workdir

CMD ["bash"]
