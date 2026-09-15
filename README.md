# Ensembl Regulation workflow containers

Dockerfiles and GitLab CI configuration for the container images used by the Ensembl Regulation
workflows. Every image is built, tested and scanned by CI, then pushed to the EBI GitLab Container
Registry.

Each image lives in its own versioned directory and is pinned to an exact tool version, so a
workflow can always pull the same image it was validated against. The *base* image is deliberately
not pinned that way — it tracks a maintained minor tag so that rebuilds pick up distribution
security updates. See [Keeping images patched](#keeping-images-patched).

## Registry

Images are published to:

```
dockerhub.ebi.ac.uk/ensreg/workflows/container-images/<image>:<tag>
```

For example:

```bash
docker pull dockerhub.ebi.ac.uk/ensreg/workflows/container-images/bedtools:2.31.0
```

CI pushes three tags per build:

| Tag | Source |
|-----|--------|
| `<version>` | the `software.version` label in the Dockerfile |
| `<version>-<digest>` | `software.version` plus the first 12 characters of the image digest, so a rebuild of the same version is still addressable |
| `latest` | only if the Dockerfile sets `software.latest_version="true"` |

The version comes from the image label, not from the directory name. If they disagree, the label
wins.

## Repository layout

```
dockerfiles/<image>/<version>/     Dockerfile, run_tests.sh, docker-compose.test.yml, any scripts
dockerfiles/.deprecated/           retired images, not built by CI
configs/gitlab-ci/<image>/<version>.yml   build/test/scan jobs for that image version
configs/gitlab-ci/container-scanning/     shared .container_scanning template
.gitlab-ci.yml                     stages and the .build / .test job templates
vulnerability-allowlist.yml        scanner findings that cannot be fixed by rebuilding
```

## Images

Versions link to their Dockerfile. The CI configuration for each is at
`configs/gitlab-ci/<image>/<version>.yml`.

### Bioinformatics tools

| Image | Versions | Base | Summary |
|-------|----------|------|---------|
| [bedgraphtobigwig](./dockerfiles/bedgraphtobigwig/) | [2.10.0](./dockerfiles/bedgraphtobigwig/2.10.0/Dockerfile) | minideb bookworm | Convert bedGraph to bigWig |
| [bedsort](./dockerfiles/bedsort/) | [v369](./dockerfiles/bedsort/v369/Dockerfile) | minideb bookworm | Sort a BED file by chrom, chromStart |
| [bedtobigbed](./dockerfiles/bedtobigbed/) | [2.10.0](./dockerfiles/bedtobigbed/2.10.0/Dockerfile) | minideb bookworm | Convert BED to bigBed |
| [bedtools](./dockerfiles/bedtools/) | [2.31.0](./dockerfiles/bedtools/2.31.0/Dockerfile) | ubuntu:22.04 | Genome arithmetic |
| [bowtie2_samtools](./dockerfiles/bowtie2_samtools/) | [2.4.5_1.15.1](./dockerfiles/bowtie2_samtools/2.4.5_1.15.1/Dockerfile) <br/> [2.4.5_1.22.1](./dockerfiles/bowtie2_samtools/2.4.5_1.22.1/Dockerfile) <br/> [2.5.4_1.22.1](./dockerfiles/bowtie2_samtools/2.5.4_1.22.1/Dockerfile) | minideb bookworm | Read alignment plus SAM/BAM handling in one image |
| [fasize](./dockerfiles/fasize/) | [v479](./dockerfiles/fasize/v479/Dockerfile) | minideb bookworm | Print total base count in FASTA files |
| [fastp](./dockerfiles/fastp/) | [0.23.2](./dockerfiles/fastp/0.23.2/Dockerfile) | ubuntu:22.04 | All-in-one FASTQ preprocessor |
| [fastqc](./dockerfiles/fastqc/) | [0.11.9](./dockerfiles/fastqc/0.11.9/Dockerfile) | alpine:3.22 | QC for high-throughput sequence data |
| [genrich](./dockerfiles/genrich/) | [0.6.1](./dockerfiles/genrich/0.6.1/Dockerfile) | minideb bookworm | Peak calling / sites of genomic enrichment |
| [moods](./dockerfiles/moods/) | [1.9.4.1](./dockerfiles/moods/1.9.4.1/Dockerfile) | python:3.10-slim | Motif Occurrence Detection Suite |
| [multiqc](./dockerfiles/multiqc/) | [1.19](./dockerfiles/multiqc/1.19/Dockerfile) <br/> [1.22](./dockerfiles/multiqc/1.22/Dockerfile) | python:3.11-slim | Aggregate analysis results into one report |
| [ngmerge](./dockerfiles/ngmerge/) | [0.3](./dockerfiles/ngmerge/0.3/Dockerfile) | minideb bookworm | Merge paired-end reads, remove adapters |
| [samtools](./dockerfiles/samtools/) | [1.15.1](./dockerfiles/samtools/1.15.1/Dockerfile) <br/> [1.22.1](./dockerfiles/samtools/1.22.1/Dockerfile) | minideb bookworm | SAM/BAM/CRAM utilities |
| [sinto_htslib](./dockerfiles/sinto_htslib/) | [0.10.1_1.22](./dockerfiles/sinto_htslib/0.10.1_1.22/Dockerfile) | minideb bookworm | Sinto single-cell tools plus HTSlib |
| [sra-toolkit](./dockerfiles/sra-toolkit/) | [3.3.0](./dockerfiles/sra-toolkit/3.3.0/Dockerfile) | debian bookworm | NCBI SRA Toolkit |
| [star](./dockerfiles/star/) | [2.7.11b](./dockerfiles/star/2.7.11b/Dockerfile) | minideb bookworm | RNA-seq aligner |
| [wiggletools](./dockerfiles/wiggletools/) | [1.2.11](./dockerfiles/wiggletools/1.2.11/Dockerfile) | ubuntu:22.04 | Operations on genome-wide numerical functions |

### Ensembl Regulation scripts

Images that ship an in-house script rather than a third-party tool. Where the language version
matters to the script, it forms the first half of the version as `<language minor>_<script
version>` — a minor series such as `3.11`, not a patch release, so the base can keep moving without
renaming the image.

| Image | Versions | Entry point | Summary |
|-------|----------|-------------|---------|
| [ensreg-gapped-peaks](./dockerfiles/ensreg-gapped-peaks/) | [3.10_0.1.0](./dockerfiles/ensreg-gapped-peaks/3.10_0.1.0/Dockerfile) | `writeGappedPeaks.py` | Gapped peaks generation |
| [ensreg-wf](./dockerfiles/ensreg-wf/) | [0.4.5](./dockerfiles/ensreg-wf/0.4.5/Dockerfile) | `ensreg-wf` | Convert sample sheets into workflow task payloads |
| [masked-regions-identification](./dockerfiles/masked-regions-identification/) | [0.1.0](./dockerfiles/masked-regions-identification/0.1.0/Dockerfile) | `maskedRegionsIdentification.R` | Masked regions identification (R 4.3) |
| [sn-barcode-correction](./dockerfiles/sn-barcode-correction/) | [0.2.0](./dockerfiles/sn-barcode-correction/0.2.0/Dockerfile) | `barcodes_correction.py` | Barcode correction for single-nucleus/-cell data |
| [sn-barcode-preprocessing](./dockerfiles/sn-barcode-preprocessing/) | [0.1.1](./dockerfiles/sn-barcode-preprocessing/0.1.1/Dockerfile) | `sn_atac_barcodes_preprocessing.py` | Barcode trimming for single-nucleus/-cell data |
| [sn-fastq-cleanup-and-update](./dockerfiles/sn-fastq-cleanup-and-update/) | [0.5.1](./dockerfiles/sn-fastq-cleanup-and-update/0.5.1/Dockerfile) | `sn_fastq_filtering_update.py` | FASTQ cleanup and whitelist filtering after barcode correction |

### Helper images

| Image | Versions | Summary |
|-------|----------|---------|
| [aws-cli](./dockerfiles/aws-cli/) | [2.33.0](./dockerfiles/aws-cli/2.33.0/Dockerfile) | AWS CLI |
| [bash](./dockerfiles/bash/) | [5.2-alpine3.22](./dockerfiles/bash/5.2-alpine3.22/Dockerfile) <br/> [5.2](./dockerfiles/bash/5.2/Dockerfile) | Shell steps in workflows |
| [python-wf-helper](./dockerfiles/python-wf-helper/) | [3.11_0.1.0](./dockerfiles/python-wf-helper/3.11_0.1.0/Dockerfile) | Python helper for workflow glue code |
| [kubectl](./dockerfiles/kubectl/) | [unversioned](./dockerfiles/kubectl/Dockerfile) | Kubernetes CLI (kubectl 1.37.0) |
| [postgres-client](./dockerfiles/postgres-client/) | [unversioned](./dockerfiles/postgres-client/Dockerfile) | `psql` and PostgreSQL 14 client tools |

`kubectl` and `postgres-client` sit directly under `dockerfiles/` with no version directory and no
CI configuration, so they are not built by the pipeline.

## Image conventions

Follow these when adding or updating an image:

- **Labels.** `software`, `software.version`, `about.summary`, `about.home`, `about.documentation`,
  and `about.license`. Add `software.latest_version="true"` to exactly one version per image — the
  newest published version — and omit it from older versions. This is what makes CI push `latest`.
  Keep `software.version` in sync with the directory name; CI reads both labels.
- **Non-root user.** Every image creates the `ensreg` user with UID/GID `8737` and runs as it. The
  fixed UID keeps file ownership consistent across workflow steps.
- **Working directory.** `/home/ensreg/workdir`, mode `777`.
- **Pin the tool, track the base.** Download an exact release of the packaged tool so the image
  matches its version tag. The *base image* is the opposite: track a maintained minor tag
  (`python:3.11-slim-bookworm`) rather than a patch tag, so rebuilds pick up distribution fixes —
  see [Keeping images patched](#keeping-images-patched).
- **Slim bases.** `bitnami/minideb`, `*-slim`, or Alpine where the tool allows it. Use a multi-stage
  build when the tool has to be compiled — see
  [bowtie2_samtools/2.5.4_1.22.1](./dockerfiles/bowtie2_samtools/2.5.4_1.22.1/Dockerfile). Keep
  compilers and `-dev` packages out of the runtime stage; see [Keeping images
  patched](#keeping-images-patched).
- **Pinned Python dependencies.** Pin the transitive packages that matter, not just the top-level
  one. `pandas==1.5.2` with an unpinned `numpy` built fine in 2023 and breaks on a rebuild today.
- **`run_tests.sh`.** Copied to `/usr/local/bin/` and made executable. A smoke test is enough
  (`bedtools --version`, `STAR --help`), with `set -uef` and `set -o xtrace` so failures surface in
  the CI log. Do not use `set -o pipefail` under `#!/bin/sh`: that works on Alpine's busybox ash but
  Debian's dash rejects it and the script exits 2 before running anything. Use `#!/bin/bash`, or
  leave `pipefail` out.

## Building and testing locally

Build:

```bash
docker build dockerfiles/multiqc/1.22
```

Run the smoke test the same way CI does:

```bash
docker compose --file dockerfiles/multiqc/1.22/docker-compose.test.yml up --build --exit-code-from sut
```

The compose file defines a single `sut` service that builds the Dockerfile and runs `run_tests.sh`:

```yaml
services:
  sut:
    build: .
    command: run_tests.sh
```

**The filename must be exactly `docker-compose.test.yml`.** The CI test job checks for that name and
falls back to a plain `docker build` when it is missing, so an image with a `docker-compose.yml` or a
`.test.yaml` is built but never actually tested.

## CI/CD pipeline

`.gitlab-ci.yml` defines the stages and the job templates; `configs/gitlab-ci/**.yml` is included
wholesale, so a per-version file is picked up as soon as it is added. It also pulls in GitLab's
SAST, dependency-scanning and secret-detection templates, which scan this repository itself rather
than the images.

| Stage | Template | What it does |
|-------|----------|--------------|
| `build` | `.build` | Builds the image, reads `software.version` from the label, pushes the version, version-digest and (conditionally) `latest` tags |
| `test` | `.test` | Runs `docker compose ... --exit-code-from sut` if `docker-compose.test.yml` exists, otherwise just rebuilds |
| `test` | `sast` | GitLab Advanced SAST over the repository (scripts and CI config), not the images |
| `secret-detection` | `secret_detection` | Scans the repository for committed credentials |
| `security-checks` | `.container_scanning` | GitLab container scanning against the pushed version and `latest` tags; allowed to fail |

Jobs run in a `docker:28.4-dind` service and retry up to twice. Each version's jobs run when that
version's own files change — its `configs/gitlab-ci/<image>/<version>.yml`, its
`dockerfiles/<image>/<version>/*`, or `.gitlab-ci.yml` — or when the pipeline is a scheduled one.
Editing one image does not rebuild the rest.

Scanning can be turned off for a pipeline by setting `CONTAINER_SCANNING_DISABLED` to `true`.

## Keeping images patched

Container scanning covers every published version tag and `latest`. Most
findings come from base-image packages, so follow four rules:

1. **Ship only what runs.** Use multi-stage builds to keep compilers, `-dev`
   packages and other build dependencies out of a slim runtime image, as in
   [moods](./dockerfiles/moods/1.9.4.1/Dockerfile) and
   [ensreg-gapped-peaks](./dockerfiles/ensreg-gapped-peaks/3.10_0.1.0/Dockerfile).
2. **Track a minor tag, not a patch tag.** Patch tags stop receiving rebuilt base
   images when superseded. For example, `python:3.11.7-slim-bookworm` was last
   pushed in February 2024, while `python:3.11-slim-bookworm` continues to receive
   updates. Both provide Debian 12 and Python 3.11, but only the minor tag stays
   current.

   Do not assume from the tag's shape — check it:

   ```bash
   docker run --rm <base> sh -c 'apt-get update -qq && apt-get -s upgrade | grep -c ^Inst'
   ```

   `python:3.10-slim-bookworm` and `python:3.11-slim-bookworm` report 0, as do
   `bitnami/minideb:bookworm`, `debian:bookworm-slim` and `ubuntu:22.04`.

3. **Upgrade at build time only when no maintained tag exists.** For example,
   `rocker/r-ver:4.3` stopped updating when R 4.3 ended, and `alpine:3.22` is
   rebuilt only for Alpine point releases. Those images use an `apt-get upgrade`
   or `apk upgrade` layer—currently
   [masked-regions-identification](./dockerfiles/masked-regions-identification/0.1.0/Dockerfile),
   [fastqc](./dockerfiles/fastqc/0.11.9/Dockerfile) and the two
   [bash](./dockerfiles/bash/) images. Avoid upgrade layers elsewhere because
   they increase image size and reduce reproducibility.

4. **Rebuild on a schedule.** Base tags and upgrade layers refresh only during a
   build. Scheduled pipelines rebuild and rescan every version because their jobs
   run when `$CI_PIPELINE_SOURCE == "schedule"`. Configure one under **Build >
   Pipeline schedules**; otherwise images rebuild only when their files change.

Base images must be on a release that still gets security updates. Debian 11
(bullseye) and Ubuntu 20.04 are both past end of life; use Debian 12 (bookworm),
Ubuntu 22.04, or a current Alpine.

### Allowlisting

Some findings cannot be fixed by rebuilding — the distribution has declared the
package not affected, or the scanner attributed the CVE to the wrong package.
Those go in [vulnerability-allowlist.yml](./vulnerability-allowlist.yml) with the
reason recorded.

Anything with an available fix must be fixed, not allowlisted. Findings that are
real but not yet fixed upstream are also left in place, so that the fix is
noticed when it ships.

## Adding an image or a new version

1. Create `dockerfiles/<image>/<version>/` with the `Dockerfile`, `run_tests.sh` and
   `docker-compose.test.yml`, following the conventions above.
2. Build and run the test locally.
3. Copy an existing `configs/gitlab-ci/<image>/<version>.yml` and replace `IMAGE_NAME`,
   `IMAGE_VERSION` and every job name and `rules:changes` path. The four jobs are
   `build-`, `test-`, `scan-<image>-<version>` and `scan-<image>-latest`.
4. When promoting a new version, move `software.latest_version="true"` off the previous version's
   Dockerfile and onto the new one.
5. Add the image to the tables above.

To retire an image, move its directory under `dockerfiles/.deprecated/` and delete its
`configs/gitlab-ci/` entry so the pipeline stops building it.
