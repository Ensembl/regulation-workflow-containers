#!/bin/sh

set -uef
set -o xtrace


psql --help
pg_dump --help
pg_dump --version
