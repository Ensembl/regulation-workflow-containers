FROM bash:5.2-alpine3.19

LABEL software="Bash"
LABEL software.version="5.2-alpine3.19"
LABEL software.latest_version="true"
LABEL about.summary="GNU Project's Bourne Again SHell"
LABEL about.home="https://tiswww.case.edu/php/chet/bash/bashtop.html"
LABEL about.documentation="https://tiswww.case.edu/php/chet/bash/README"
LABEL about.license="https://www.gnu.org/licenses/gpl-3.0.html"

LABEL maintainer="David Urbina-Gómez"
LABEL maintainer.email="durbina@ebi.ac.uk"

RUN apk add --no-cache tar pigz

RUN addgroup -g 8737 ensreg \
    && adduser -u 8737 -G ensreg -D ensreg

USER 8737

RUN mkdir /home/ensreg/workdir \
    && chmod 777 /home/ensreg/workdir

WORKDIR /home/ensreg/workdir

CMD ["bash"]
