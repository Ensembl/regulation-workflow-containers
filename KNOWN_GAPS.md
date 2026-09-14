# Known gaps

Recorded rather than fixed, because each needs a decision or touches published tags.

**16 of 32 image versions are never actually tested by CI.** The `.test` job looks for
`docker-compose.test.yml` by that exact name and silently falls back to a plain `docker build`
otherwise, so these are built but their `run_tests.sh` never runs:

- Wrong extension: `bedtools/2.31.0` (`docker-compose.test.yaml`), `moods/1.9.4.1`
  (`docker-compose.yaml`)
- Named `docker-compose.yml`: `aws-cli`, both `bash` images, `bedgraphtobigwig`,
  `ensreg-gapped-peaks`, `masked-regions-identification`, `python-wf-helper`, both
  `samtools`, `sn-barcode-correction`, `sn-fastq-cleanup-and-update`, `wiggletools`
- No compose file at all: `star/2.7.11b`, `sn-barcode-preprocessing/0.1.1`

**12 `run_tests.sh` scripts exit 2 before running anything** — they combine `#!/bin/sh` with
`set -o pipefail`, which Debian's dash rejects. Alpine-based images are unaffected. Masked by the
gap above: none of these currently run in CI.

**`samtools/1.15.1` never copies `run_tests.sh` into the image**, so its test could not run even
with a correct compose file.

**The two `bash` images are near-duplicates.** `bash:5.2` and `bash:5.2-alpine3.22` now resolve to
the same upstream image (bash 5.2.37 on Alpine 3.22); the only difference left is that `5.2` also
installs `jq` and `curl`. The names imply a base difference that no longer exists — worth collapsing
into one image, at the cost of another tag change.

**`kubectl` pins `bitnami/kubectl:1.23`** and `postgres-client` has no version directory. Neither
has a CI configuration, so neither is built or scanned.

**`configs/gitlab-ci/masked-regions-indentification/`** is misspelled. Harmless — the include is a
glob and `IMAGE_NAME` inside the file is correct — but it does not match the image name.
