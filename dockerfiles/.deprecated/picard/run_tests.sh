#!/bin/sh

set -uef
set -o pipefail
set -o xtrace

java -jar /usr/picard/picard.jar -h

