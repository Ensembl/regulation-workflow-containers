import csv
import json
from collections import defaultdict
from enum import Enum
from pathlib import Path

import logfire
from typing import Annotated

import typer
import polars as pl

from pydantic import (
    BaseModel,
    Field,
    ByteSize,
    conint,
    conlist,
    RootModel,
    ConfigDict,
    ValidationError,
)

import os

## Validates the following regex is met: (E|D|S)RX[0-9]{6,}
ENAExperimentAccession = Annotated[str, Field(pattern=r"^(E|D|S)RX[0-9]{6,}$")]

## Validates the following regex is met: (E|D|S)RR[0-9]{6,}
ENARunAccession = Annotated[str, Field(pattern=r"^(E|D|S)RR[0-9]{6,}$")]

# Validates the following regex is met:
ENCODEExperimentAccession = Annotated[
    str, Field(pattern=r"^ENCSR[0-9]{3}[A-Z]{3}$")]


class GeneAnnotationParameter(BaseModel):
    provider: str
    version: str


class StarIndexParameter(BaseModel):
    path: str
    size: ByteSize

class Bowtie2IndexParameter(BaseModel):
    path: str
    size: ByteSize = Field(..., description="Size of the Bowtie2 index in bytes")

class ReadFileParameter(BaseModel):
    url: str
    bytes: ByteSize
    md5: str


class RunMode(str, Enum):
    single_cell = "single-cell"
    paired_end = "paired-end"
    single_end = "single-cell"


class ScRNASeqTask(BaseModel):
    assembly_name: str = Field(
        ...,
        description="Genome assembly name",
        examples=["GRCh38", "GRCm39", "IRGSP-1.0"],
    )
    gene_annotation: GeneAnnotationParameter = Field(
        ...,
        description="Gene annotation information",
    )
    star_index: StarIndexParameter = Field(
        ...,
        description="STAR index reference",
    )
    inclusion_list: str = Field(
        ...,
        description="Path to barcode inclusion list",
        examples=["inclusion-list/gex_737K-arc-v1.txt"],
    )
    run_accession: ENARunAccession
    bio_reads: ReadFileParameter = Field(
        ...,
        description="Biological reads file",
        alias="bio_reads",
    )
    barcode_reads: ReadFileParameter = Field(
        ...,
        description="Barcode reads file",
        alias="barcode_reads",
    )
    output_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path)",
    )
    threads: conint(ge=1, le=32) = Field(
        default=9,
        description="Number of threads for STAR alignment",
    )

    def to_wf_parameters(self) -> dict[str, str]:
        return {
            "barcode_reads_url": self.barcode_reads.url,
            "bio_reads_url": self.bio_reads.url,
            "barcode_file_size": str(self.barcode_reads.bytes),
            "bio_file_size": str(self.bio_reads.bytes),
            "reference_file_size": str(self.star_index.size),
            "star_index_s3_key": self.star_index.path,
            "barcode_inclusion_s3_key": self.inclusion_list,
            "output_prefix": self.output_prefix,
            "threads": str(self.threads),
            "s3_output_key_prefix": self.output_prefix,
        }


class ENAPairedRun(BaseModel):
    # TODO: Improve type annotations with Gt, url, bytes, pattern, etc.
    accession: ENARunAccession
    read1_reads_url: str
    read1_file_size: int
    read1_md5: str | None
    read2_reads_url: str
    read2_file_size: int
    read2_md5: str | None


class ENASingleRun(BaseModel):
    accession: ENARunAccession
    read1_reads_url: str
    read1_file_size: int
    read1_md5: str | None


class ENARuns(RootModel[list[ENAPairedRun | ENASingleRun]]):
    """Collection of bulk RNA-seq tasks from a sample sheet"""
    ...

class ENARunWithoutPath(BaseModel):
    accession: ENARunAccession
    fastq_bytes: ByteSize

class ENARunsWithoutPaths(RootModel[list[ENARunWithoutPath]]):
    """Collection of runs without file paths, used for task grouping"""
    ...

class ENAScATACSeqTask(BaseModel):
    experiment_accession: ENAExperimentAccession
    runs: ENARunsWithoutPaths
    run_mode: RunMode = Field(
        default=RunMode.single_cell,
        description="Run mode for scATAC-seq (default: single-cell)",
    )
    bowtie2_index: Bowtie2IndexParameter = Field(
        ...,
        description="Bowtie2 index reference")

    s3_output_key_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path)",
    )

    def total_file_size(self) -> int:
        """Calculate total bytes of files to be processed."""
        return sum(run.fastq_bytes for run in self.runs)

    def to_wf_parameters(self) -> dict[str, str]:
        """Serialize to Argo Wfs parameter dict."""
        # TODO: Simplify names, need to update wf first

        return {
            "experiment_accession": self.experiment_accession,
            "experiment_runs_info": {"runs": self.runs.model_dump()},
            "total_files_size": self.total_file_size(),
            "run_mode": str(self.run_mode.value),
            "inclusion_list_file_key": self.inclusion_list,
            "bowtie2_index_key": self.bowtie2_index.path,
            "bowtie2_index_basename": "genome",
            "s3_output_key_prefix": self.s3_output_key_prefix,
        }


class ENAScATACSeqSample(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    assembly_name: str = Field(..., alias="assembly.name", description=(
        "Genome assembly"))

    bowtie2_index_path: str = Field(..., alias="bowtie2_index.path")
    bowtie2_index_size: ByteSize = Field(..., alias="bowtie2_index.size")

    inclusion_list: str = Field(..., description=(
        "Path to barcode inclusion list"))

    experiment_accession: ENAExperimentAccession
    run_accession: ENARunAccession

    run_fastq_bytes: int = Field(..., alias="fastq_bytes")

    output_prefix: str = Field(..., description="Output file prefix (S3 path)")


class ENAScATACSeqSampleSheet(RootModel[list[ENAScATACSeqSample]]):
    """Sample sheet for ENA scATAC-seq data."""

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index: int) -> ENAScATACSeqSample:
        return self.root[index]

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "ENAScATACSeqSampleSheet":
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise ValueError(f"CSV file not found: {csv_path}")

        samples = []
        errors: dict[int, ValidationError] = {}

        try:
            with csv_path.open(newline="") as f:
                for row_num, row in enumerate(csv.DictReader(f), start=2):
                    row = {k: (v if v != "" else None) for k, v in row.items()}
                    try:
                        samples.append(ENAScATACSeqSample.model_validate(row))
                    except ValidationError as e:
                        errors[row_num] = e
        except OSError as e:
            raise ValueError(f"Failed to read CSV '{csv_path}': {e}") from e

        if errors:
            error_summary = "\n\n".join(
                f"Row {row_num}:\n{error}" for row_num, error in errors.items()
            )
            raise ValueError(
                f"Sample sheet validation failed:\n\n{error_summary}"
            )

        return cls(samples)

    def to_sc_atac_seq_tasks(self) -> list[ENAScATACSeqTask]:
        groups: dict[str, list[ENAScATACSeqSample]] = defaultdict(list)
        for sample in self:
            groups[sample.experiment_accession].append(sample)

        tasks = []
        for experiment_accession, samples in groups.items():
            rep = samples[0]

            runs = ENARunsWithoutPaths([
                ENARunWithoutPath(
                    accession=sample.run_accession,
                    fastq_bytes=sample.run_fastq_bytes,
                )
                for sample in samples
            ])

            tasks.append(
                ENAScATACSeqTask(
                    experiment_accession=rep.experiment_accession,
                    runs=runs,
                    run_mode=RunMode.single_cell,
                    bowtie2_index=Bowtie2IndexParameter(
                        path=rep.bowtie2_index_path,
                        size=rep.bowtie2_index_size,
                    ),
                    s3_output_key_prefix=rep.output_prefix,
                )
            )

        return tasks

    def to_json(self, path: Path | str) -> None:
        tasks = self.to_sc_atac_seq_tasks()
        json_data = [t.to_wf_parameters() for t in tasks]
        Path(path).write_text(json.dumps(json_data, indent=4))

class ENABulkRNASeqTask(BaseModel):
    runs: ENARuns
    run_mode: RunMode
    star_index: StarIndexParameter = Field(
        ...,
        description="STAR index reference",
    )
    s3_output_key_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path)",
    )
    threads: conint(ge=1, le=32) = Field(
        default=9,
        description="Number of threads for STAR alignment",
    )

    def to_wf_parameters(self) -> dict[str, str]:
        """Serialize to Argo Wfs parameter dict."""
        return {
            "runs": self.runs.model_dump(),
            "run_mode": str(self.run_mode.value),
            "star_index_s3_key": self.star_index.path,
            "reference_file_size": str(self.star_index.size),
            "threads": str(self.threads),
            "s3_output_key_prefix": self.s3_output_key_prefix,
        }


class ENABulkRNASeqSample(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    assembly_name: str = Field(..., description="Genome assembly name")

    gene_annotation_provider: str = Field(
        ...,
        alias="gene_annotation.provider"
    )
    gene_annotation_version: str = Field(..., alias="gene_annotation.version")

    star_index_path: str = Field(..., alias="star_index.path")
    star_index_size: ByteSize = Field(..., alias="star_index.size")

    experiment_accession: ENAExperimentAccession
    run_accession: ENARunAccession

    read_1_url: str = Field(..., alias="read_1.url")
    read_1_bytes: ByteSize = Field(..., alias="read_1.bytes")
    read_1_md5: str | None = Field(None, alias="read_1.md5")

    read_2_url: str | None = Field(None, alias="read_2.url")
    read_2_bytes: ByteSize | None = Field(None, alias="read_2.bytes")
    read_2_md5: str | None = Field(None, alias="read_2.md5")

    output_prefix: str = Field(..., description="Output file prefix (S3 path)")
    threads: conint(ge=1, le=32) = Field(default=9)


class BulkRNASeqSampleSheet(RootModel[list[ENABulkRNASeqSample]]):
    """Collection of bulk RNA-seq tasks from a sample sheet"""
    ...

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index: int) -> ENABulkRNASeqSample:
        return self.root[index]

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "BulkRNASeqSampleSheet":
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise ValueError(f"CSV file not found: {csv_path}")

        samples = []
        errors: dict[int, ValidationError] = {}

        try:
            with csv_path.open(newline="") as f:
                for row_num, row in enumerate(csv.DictReader(f), start=2):
                    row = {k: (v if v != "" else None) for k, v in row.items()}
                    try:
                        samples.append(ENABulkRNASeqSample.model_validate(row))
                    except ValidationError as e:
                        errors[row_num] = e
        except OSError as e:
            raise ValueError(f"Failed to read CSV '{csv_path}': {e}") from e

        if errors:
            error_summary = "\n\n".join(
                f"Row {row_num}:\n{error}" for row_num, error in errors.items()
            )
            raise ValueError(
                f"Sample sheet validation failed:\n\n{error_summary}"
            )

        return cls(samples)

    def to_bulk_rna_seq_tasks(self) -> list[ENABulkRNASeqTask]:
        groups: dict[str, list[ENABulkRNASeqSample]] = defaultdict(list)
        for sample in self:
            groups[sample.experiment_accession].append(sample)

        tasks = []
        for experiment_accession, samples in groups.items():
            rep = samples[0]

            runs: list[ENAPairedRun | ENASingleRun] = []
            for sample in samples:
                if sample.read_2_url is not None:
                    runs.append(
                        ENAPairedRun(
                            accession=sample.run_accession,
                            read1_reads_url=sample.read_1_url,
                            read1_file_size=sample.read_1_bytes,
                            read1_md5=sample.read_1_md5,
                            read2_reads_url=sample.read_2_url,
                            read2_file_size=sample.read_2_bytes,
                            read2_md5=sample.read_2_md5,
                        )
                    )
                else:
                    runs.append(
                        ENASingleRun(
                            accession=sample.run_accession,
                            read1_reads_url=sample.read_1_url,
                            read1_file_size=sample.read_1_bytes,
                            read1_md5=sample.read_1_md5,
                        )
                    )

            run_types = {type(r) for r in runs}
            if len(run_types) > 1:
                raise ValueError(
                    f"Mixed paired/single-end runs in experiment "
                    f"{experiment_accession!r}"
                )
            run_mode = RunMode.paired_end if run_types == {ENAPairedRun} else RunMode.single_end

            tasks.append(
                ENABulkRNASeqTask(
                    runs=ENARuns(runs),
                    run_mode=run_mode,
                    star_index=StarIndexParameter(
                        path=rep.star_index_path,
                        size=rep.star_index_size,
                    ),
                    s3_output_key_prefix=rep.output_prefix,
                    threads=rep.threads,
                )
            )

        return tasks

    def to_json(self, path: Path | str) -> None:
        tasks = self.to_bulk_rna_seq_tasks()
        json_data = [t.to_wf_parameters() for t in tasks]
        Path(path).write_text(json.dumps(json_data, indent=4))


class ScRNASeqSampleSheet(BaseModel):
    """Collection of scRNA-seq tasks from a sample sheet"""

    tasks: conlist(ScRNASeqTask, min_length=1) = Field(
        ...,
        description="List of scRNA-seq alignment tasks",
    )

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "ScRNASeqSampleSheet":
        """
        Parse sample sheet CSV into validated ScRNASeqTask objects.

        Args:
            csv_path: Path to the CSV file

        Returns:
            ScRNASeqSampleSheet with validated tasks

        Raises:
            ValueError: If CSV parsing or validation fails
        """
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        tasks = []
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(
                    reader, start=2
            ):  # Start at 2 (header is row 1)
                try:
                    # Map CSV columns to model fields
                    # Handle the inconsistent column naming in the CSV
                    task_data = {
                        "assembly_name": row["assembly_name"],
                        "gene_annotation": {
                            "provider": row["gene_annotation.provider"],
                            "version": row["gene_annotation.version"],
                        },
                        "star_index": {
                            "path": row["star_index.path"],
                            "size": int(row["star_index.size"]),
                        },
                        "inclusion_list": row["inclusion_list"],
                        "run_accession": row["run_accession"],
                        "bio_reads": {
                            "url": row["bio_reads.url"],
                            "bytes": int(row["bio_reads.bytes"]),
                            "md5": row["bio_reads.md5"],
                        },
                        "barcode_reads": {
                            "url": row["barcode_reads.url"],
                            "bytes": int(row["barcode_reads.bytes"]),
                            "md5": row["barcode_reads.md5"],
                        },
                        "output_prefix": row["output_prefix"],
                        "threads": int(row["threads"]),
                    }

                    task = ScRNASeqTask(**task_data)
                    tasks.append(task)

                except Exception as e:
                    raise ValueError(
                        f"Error parsing row {row_num} (accession: "
                        f"{row.get('run_accession', 'unknown')}): {e}"
                    ) from e

        return cls(tasks=tasks)

    def to_json(self, file_name) -> str:
        """Serialize the sample sheet to JSON format."""
        with open(file_name, "w") as f:
            json_data = [t.to_wf_parameters() for t in self.tasks]
            json.dump(json_data, f, indent=4)


app = typer.Typer()


class SampleSheetType(str, Enum):
    SCATAC_SEQ = "sc-atac-seq"
    SCRNA_SEQ = "sc-rna-seq"
    BULK_RNA_SEQ = "bulk-rna-seq"


def _parse_scatac_seq_sample_sheet(sample_sheet: Path) -> ENAScATACSeqSampleSheet:
    return ENAScATACSeqSampleSheet.from_csv(sample_sheet)


def _parse_scrna_seq_sample_sheet(sample_sheet: Path) -> ScRNASeqSampleSheet:
    return ScRNASeqSampleSheet.from_csv(sample_sheet)


def _parse_bulk_rna_seq_sample_sheet(
    sample_sheet: Path
    ) -> BulkRNASeqSampleSheet:
    return BulkRNASeqSampleSheet.from_csv(sample_sheet)


@app.command("parse")
@logfire.instrument("'parse' sample sheet: {sample_sheet=}")
def parse_sample_sheet(
    sample_sheet_type: SampleSheetType,
    sample_sheet_file: Path = typer.Argument(
        ...,
        help="Path to the sample sheet CSV file"
    )
) -> int:
    output_json = sample_sheet_file.stem + ".json"

    logfire.info(f"Parsing sample sheet CSV: {sample_sheet_file}")

    match sample_sheet_type:
        case SampleSheetType.SCATAC_SEQ:
            sample_sheet = _parse_scatac_seq_sample_sheet(sample_sheet_file)
        case SampleSheetType.SCRNA_SEQ:
            sample_sheet = _parse_scrna_seq_sample_sheet(sample_sheet_file)
        case SampleSheetType.BULK_RNA_SEQ:
            sample_sheet = _parse_bulk_rna_seq_sample_sheet(sample_sheet_file)
        case _:
            raise ValueError(
                f"Unsupported sample sheet type: {sample_sheet_type}"
                )

    logfire.info(f"Parsed {len(sample_sheet)} tasks from sample sheet.")

    with open('num_tasks.txt', 'w') as f:
        f.write(str(len(sample_sheet)))

    print(f"Payload:\n{sample_sheet.model_dump_json(indent=4)}")

    logfire.info(f"Serializing sample sheet to JSON: {output_json}")

    sample_sheet.to_json(output_json)

    os.system('ls -altrh .')

    return 0
