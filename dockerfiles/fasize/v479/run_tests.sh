#!/bin/sh

set -uef
set -o xtrace

test_fasta="$(mktemp)"
trap 'rm -f "${test_fasta}"' EXIT

printf '>first\nACGT\n>second\nAACCGG\n' > "${test_fasta}"
faSize "${test_fasta}" | grep -Fq '10 bases (0 N'
