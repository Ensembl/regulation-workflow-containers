FROM bash:5.2.21

LABEL software="Bash"
LABEL software.version="5.2.21"
LABEL about.summary="GNU Project's Bourne Again SHell"
LABEL about.home="https://tiswww.case.edu/php/chet/bash/bashtop.html"
LABEL about.documentation="https://tiswww.case.edu/php/chet/bash/README"
LABEL about.license="https://www.gnu.org/licenses/gpl-3.0.html"

LABEL mantainer="David Urbina-Gómez"
LABEL mantainer.email="durbina@ebi.ac.uk"

RUN apk add --no-cache tar pigz

RUN  mkdir /results

CMD ["bash"]
