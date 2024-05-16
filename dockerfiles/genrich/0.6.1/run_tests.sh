#!/bin/sh

set -uef
set -o xtrace

Genrich -t mt.queryname_sorted.bam -o sample.narrowPeak  -v