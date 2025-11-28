#!/bin/sh

set -uef
set -o pipefail
set -o xtrace

python barcodes_correction.py --help

python filter_invalid_barcodes.py --help
