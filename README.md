# Ensembl Regulation workflow container images

Dockerfiles and GitLab CI configuration for the container images used by the Ensembl Regulation
workflows. Every image is built, tested and scanned by CI, then pushed to the EBI GitLab Container
Registry.

Each image lives in its own versioned directory and is pinned to an exact tool version, so a
workflow can always pull the same image it was validated against.

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
```

## Images

Versions link to their Dockerfile. The CI configuration for each is at
`configs/gitlab-ci/<image>/<version>.yml`. A `†` marks the version currently tagged `latest`.

### Bioinformatics tools

| Image | Versions | Base | Summary |
|-------|----------|------|---------|
| [bedgraphtobigwig](./dockerfiles/bedgraphtobigwig/) | [2.10.0](./dockerfiles/bedgraphtobigwig/2.10.0/Dockerfile) | minideb bookworm | Convert bedGraph to bigWig |
| [bedsort](./dockerfiles/bedsort/) | [v369](./dockerfiles/bedsort/v369/Dockerfile) | minideb bullseye | Sort a BED file by chrom, chromStart |
| [bedtobigbed](./dockerfiles/bedtobigbed/) | [2.10.0](./dockerfiles/bedtobigbed/2.10.0/Dockerfile) | minideb bullseye | Convert BED to bigBed |
| [bedtools](./dockerfiles/bedtools/) | [2.31.0](./dockerfiles/bedtools/2.31.0/Dockerfile) † | ubuntu:22.04 | Genome arithmetic |
| [bowtie2_samtools](./dockerfiles/bowtie2_samtools/) | [2.4.5_1.15.1](./dockerfiles/bowtie2_samtools/2.4.5_1.15.1/Dockerfile) <br/> [2.4.5_1.22.1](./dockerfiles/bowtie2_samtools/2.4.5_1.22.1/Dockerfile) <br/> [2.5.4_1.22.1](./dockerfiles/bowtie2_samtools/2.5.4_1.22.1/Dockerfile) | minideb bullseye | Read alignment plus SAM/BAM handling in one image |
| [fasize](./dockerfiles/fasize/) | [v459](./dockerfiles/fasize/v459/Dockerfile) | minideb bullseye | Print total base count in FASTA files |
| [fastp](./dockerfiles/fastp/) | [0.23.2](./dockerfiles/fastp/0.23.2/Dockerfile) | ubuntu:20.04 | All-in-one FASTQ preprocessor |
| [fastqc](./dockerfiles/fastqc/) | [0.11.9](./dockerfiles/fastqc/0.11.9/Dockerfile) | alpine:3.12 | QC for high-throughput sequence data |
| [genrich](./dockerfiles/genrich/) | [0.6.1](./dockerfiles/genrich/0.6.1/Dockerfile) † | minideb bookworm | Peak calling / sites of genomic enrichment |
| [moods](./dockerfiles/moods/) | [1.9.4.1](./dockerfiles/moods/1.9.4.1/Dockerfile) | python:3.10.7 | Motif Occurrence Detection Suite |
| [multiqc](./dockerfiles/multiqc/) | [1.19](./dockerfiles/multiqc/1.19/Dockerfile) <br/> [1.22](./dockerfiles/multiqc/1.22/Dockerfile) † | python:3.11 | Aggregate analysis results into one report |
| [ngmerge](./dockerfiles/ngmerge/) | [0.3](./dockerfiles/ngmerge/0.3/Dockerfile) | minideb bullseye | Merge paired-end reads, remove adapters |
| [samtools](./dockerfiles/samtools/) | [1.15.1](./dockerfiles/samtools/1.15.1/Dockerfile) <br/> [1.22.1](./dockerfiles/samtools/1.22.1/Dockerfile) | minideb bullseye | SAM/BAM/CRAM utilities |
| [sinto_htslib](./dockerfiles/sinto_htslib/) | [0.10.1_1.22](./dockerfiles/sinto_htslib/0.10.1_1.22/Dockerfile) | minideb bullseye | Sinto single-cell tools plus HTSlib |
| [sra-toolkit](./dockerfiles/sra-toolkit/) | [3.3.0](./dockerfiles/sra-toolkit/3.3.0/Dockerfile) | debian bookworm | NCBI SRA Toolkit |
| [star](./dockerfiles/star/) | [2.7.11b](./dockerfiles/star/2.7.11b/Dockerfile) † | minideb bookworm | RNA-seq aligner |
| [wiggletools](./dockerfiles/wiggletools/) | [1.2.11](./dockerfiles/wiggletools/1.2.11/Dockerfile) | ubuntu:20.04 | Operations on genome-wide numerical functions |

### Ensembl Regulation scripts

Images that ship an in-house script rather than a third-party tool. The version is
`<language version>_<script version>` where both matter.

| Image | Versions | Entry point | Summary |
|-------|----------|-------------|---------|
| [ensreg-gapped-peaks](./dockerfiles/ensreg-gapped-peaks/) | [3.10.12_0.1.0](./dockerfiles/ensreg-gapped-peaks/3.10.12_0.1.0/Dockerfile) | `writeGappedPeaks.py` | Gapped peaks generation |
| [masked-regions-identification](./dockerfiles/masked-regions-identification/) | [0.1.0](./dockerfiles/masked-regions-identification/0.1.0/Dockerfile) | `maskedRegionsIdentification.R` | Masked regions identification (R 4.3.0) |
| [sn-barcode-correction](./dockerfiles/sn-barcode-correction/) | [0.2.0](./dockerfiles/sn-barcode-correction/0.2.0/Dockerfile) | `barcodes_correction.py` | Barcode correction for single-nucleus/-cell data |
| [sn-barcode-preprocessing](./dockerfiles/sn-barcode-preprocessing/) | [0.1.1](./dockerfiles/sn-barcode-preprocessing/0.1.1/Dockerfile) | `sn_atac_barcodes_preprocessing.py` | Barcode trimming for single-nucleus/-cell data |
| [sn-fastq-cleanup-and-update](./dockerfiles/sn-fastq-cleanup-and-update/) | [0.5.1](./dockerfiles/sn-fastq-cleanup-and-update/0.5.1/Dockerfile) | `sn_fastq_filtering_update.py` | FASTQ cleanup and whitelist filtering after barcode correction |

### Helper images

| Image | Versions | Summary |
|-------|----------|---------|
| [aws-cli](./dockerfiles/aws-cli/) | [2.33.0](./dockerfiles/aws-cli/2.33.0/Dockerfile) | AWS CLI |
| [bash](./dockerfiles/bash/) | [5.2-alpine3.19](./dockerfiles/bash/5.2-alpine3.19/Dockerfile) † <br/> [5.2.21](./dockerfiles/bash/5.2.21/Dockerfile) | Shell steps in workflows |
| [python-wf-helper](./dockerfiles/python-wf-helper/) | [3.11.7_0.1.0](./dockerfiles/python-wf-helper/3.11.7_0.1.0/Dockerfile) | Python helper for workflow glue code |
| [kubectl](./dockerfiles/kubectl/) | [unversioned](./dockerfiles/kubectl/Dockerfile) | Kubernetes CLI (bitnami/kubectl 1.23) |
| [postgres-client](./dockerfiles/postgres-client/) | [unversioned](./dockerfiles/postgres-client/Dockerfile) | `psql` and PostgreSQL 14 client tools |

`kubectl` and `postgres-client` sit directly under `dockerfiles/` with no version directory and no
CI configuration, so they are not built by the pipeline.

## Image conventions

Follow these when adding or updating an image:

- **Labels.** `software`, `software.version`, `about.summary`, `about.home`, `about.documentation`,
  `about.license`, `maintainer`, `maintainer.email`. Add `software.latest_version="true"` on exactly
  one version per image — that is what makes CI push `latest`. Keep `software.version` in sync with
  the directory name; CI reads the label.
- **Non-root user.** Every image creates the `ensreg` user with UID/GID `8737` and runs as it. The
  fixed UID keeps file ownership consistent across workflow steps.
- **Working directory.** `/home/ensreg/workdir`, mode `777`.
- **Pinned versions.** Download a specific release; do not track a moving tag.
- **Slim bases.** `bitnami/minideb`, `*-slim`, or Alpine where the tool allows it. Use a multi-stage
  build when the tool has to be compiled — see
  [bowtie2_samtools/2.5.4_1.22.1](./dockerfiles/bowtie2_samtools/2.5.4_1.22.1/Dockerfile).
- **`run_tests.sh`.** Copied to `/usr/local/bin/` and made executable. A smoke test is enough
  (`bedtools --version`, `STAR --help`), with `set -uef` and `set -o xtrace` so failures surface in
  the CI log.

## Building and testing locally

Build:

```bash
docker build dockerfiles/bedtools/2.31.0
```

Run the smoke test the same way CI does:

```bash
docker compose --file dockerfiles/bedtools/2.31.0/docker-compose.test.yml up --build --exit-code-from sut
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

`.gitlab-ci.yml` defines three stages and the job templates; `configs/gitlab-ci/**.yml` is included
wholesale, so a per-version file is picked up as soon as it is added.

| Stage | Template | What it does |
|-------|----------|--------------|
| `build` | `.build` | Builds the image, reads `software.version` from the label, pushes the version, version-digest and (conditionally) `latest` tags |
| `test` | `.test` | Runs `docker compose ... --exit-code-from sut` if `docker-compose.test.yml` exists, otherwise just rebuilds |
| `security-checks` | `.container_scanning` | GitLab container scanning against the pushed version and `latest` tags; allowed to fail |

Jobs run in a `docker:28.4-dind` service and retry up to twice. Each version's jobs only run when
that version's own files change — its `configs/gitlab-ci/<image>/<version>.yml`, its
`dockerfiles/<image>/<version>/*`, or `.gitlab-ci.yml`. Editing one image does not rebuild the rest.

Scanning can be turned off for a pipeline by setting `CONTAINER_SCANNING_DISABLED` to `true`.

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
