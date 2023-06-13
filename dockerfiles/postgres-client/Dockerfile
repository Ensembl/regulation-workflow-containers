FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y \
    locales \
    postgresql-client-14 \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
	&& localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

COPY run_tests.sh /usr/local/bin/

RUN  chmod 755 /usr/local/bin/run_tests.sh \
     && mkdir /results

CMD ["psql"]