# ensreg-wf 0.4.5

`ensreg-wf` validates CSV sample sheets and converts them into JSON task payloads for Ensembl
Regulation workflows. It prepares workflow input only; it does not submit or run workflows.

## Supported sample sheets

Pass one of these values to `ensreg-wf parse`:

| Type | Behaviour |
|------|-----------|
| `sc-atac-seq` | Parses ENA/SRA or ENCODE input, detected from the CSV headers |
| `pseudobulk-peak-calling` | Groups alignment rows by experiment name |
| `sc-rna-seq` | Groups ENA runs by experiment accession |
| `bulk-rna-seq` | Groups ENA runs by experiment accession |
| `multiome` | Converts each row into one task |

Grouped sample sheets can therefore produce fewer tasks than input rows.

## Usage

The container runs as the non-root `ensreg` user and uses `/home/ensreg/workdir` as its working
directory. Mount the directory containing the sample sheet and run:

```bash
docker run --rm \
  --volume "$PWD:/home/ensreg/workdir" \
  dockerhub.ebi.ac.uk/ensreg/workflows/container-images/ensreg-wf:0.4.5 \
  parse sc-atac-seq samples.csv
```

For an input named `samples.csv`, the command writes two files in the working directory:

- `samples.json`: the validated workflow task payloads.
- `num_tasks.txt`: the number of tasks in `samples.json`.

Validation failures include the affected CSV row where possible and return a non-zero exit code.
Run `ensreg-wf --help` or `ensreg-wf parse --help` for command help.

## Build locally

The Python and application versions are supplied by CI as build arguments. Use the same arguments
for a local build:

```bash
docker build \
  --build-arg PYTHON_VERSION=3.13 \
  --build-arg SOFTWARE_VERSION=0.4.5 \
  --tag ensreg-wf:0.4.5 \
  dockerfiles/ensreg-wf/0.4.5
```

The build fails if `SOFTWARE_VERSION` does not match the version declared in `pyproject.toml`.
