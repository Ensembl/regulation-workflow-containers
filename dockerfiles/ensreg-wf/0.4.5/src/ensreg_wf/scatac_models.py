import csv
import json
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Annotated

from pydantic import (
    BaseModel,
    ByteSize,
    ConfigDict,
    Field,
    RootModel,
    ValidationError,
    conint,
)

from .common_models import (
    ENAExperimentAccession,
    ENARunAccession,
    RunMode,
)


# Validates the following regex is met:
ENCODEExperimentAccession = Annotated[
    str, Field(pattern=r"^ENCSR[0-9]{3}[A-Z]{3}$")]

ENCODEFileAccession = Annotated[
    str, Field(pattern=r"^ENCFF[0-9]{3}[A-Z]{3}$")]

ENCODERunAccession = Annotated[
    str, Field(pattern=r"^ENCSR[0-9]{3}[A-Z]{3}-[0-9]+$")]


class Bowtie2IndexParameter(BaseModel):
    path: str
    basename: str = Field(
        default="genome",
        description="Basename of the Bowtie2 index files",
    )
    size: ByteSize = Field(..., description="Size of the Bowtie2 index in bytes")

class ENARunWithoutPath(BaseModel):
    accession: ENARunAccession
    fastq_bytes: ByteSize

class ENARunsWithoutPaths(RootModel[list[ENARunWithoutPath]]):
    """Collection of runs without file paths, used for task grouping"""
    ...

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)

class ENAScATACSeqTask(BaseModel):
    experiment_accession: ENAExperimentAccession
    runs: ENARunsWithoutPaths
    run_mode: RunMode = Field(
        default=RunMode.single_cell,
        description="Run mode for scATAC-seq (default: single-cell)",
    )
    inclusion_list: str = Field(
        ...,
        description="Path to inclusion list file",
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
            "bowtie2_index_basename": self.bowtie2_index.basename,
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
                    inclusion_list=rep.inclusion_list,
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


class ENCODEFileOutputType(str, Enum):
    reads = "reads"
    index_reads = "index reads"


class ENCODEScATACRun(BaseModel):
    accession: ENCODERunAccession
    read1_reads_url: str
    read2_reads_url: str
    index_reads_url: str
    fastq_bytes: int


class ENCODEScATACRuns(RootModel[list[ENCODEScATACRun]]):
    """Collection of synthetic ENCODE scATAC-seq runs."""

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)


class ENCODEScATACSeqTask(BaseModel):
    series_accession: ENCODEExperimentAccession
    experiment_accession: ENCODEExperimentAccession
    runs: ENCODEScATACRuns
    run_mode: RunMode = Field(
        default=RunMode.single_cell,
        description="Run mode for scATAC-seq (default: single-cell)",
    )
    inclusion_list: str = Field(
        ...,
        description="Path to inclusion list file",
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
        return {
            "series_accession": self.series_accession,
            "experiment_accession": self.experiment_accession,
            "experiment_runs_info": {"runs": self.runs.model_dump()},
            "total_files_size": self.total_file_size(),
            "run_mode": str(self.run_mode.value),
            "inclusion_list_file_key": self.inclusion_list,
            "bowtie2_index_key": self.bowtie2_index.path,
            "bowtie2_index_basename": self.bowtie2_index.basename,
            "s3_output_key_prefix": self.s3_output_key_prefix,
        }


class ENCODEScATACSeqSample(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    assembly_name: str = Field(..., alias="assembly.name", description=(
        "Genome assembly"))

    bowtie2_index_path: str = Field(..., alias="bowtie2_index.path")
    bowtie2_index_basename: str = Field(..., alias="bowtie2_index.basename")
    bowtie2_index_size: ByteSize = Field(..., alias="bowtie2_index.size")

    inclusion_list: str = Field(..., description=(
        "Path to barcode inclusion list"))

    series_accession: ENCODEExperimentAccession
    experiment_accession: ENCODEExperimentAccession

    file_accession: ENCODEFileAccession = Field(..., alias="file.accession")
    file_output_type: ENCODEFileOutputType = Field(
        ...,
        alias="file.output_type",
    )
    file_paired_end: conint(ge=1, le=2) | None = Field(
        None,
        alias="file.paired_end",
    )
    file_index: ENCODEFileAccession | None = Field(None, alias="file.index")

    fastq_bytes: ByteSize = Field(..., alias="file.fastq_bytes")
    file_url: str = Field(..., alias="file.url")

    output_prefix: str = Field(..., description="Output file prefix (S3 path)")


class ENCODEScATACSeqSampleSheet(RootModel[list[ENCODEScATACSeqSample]]):
    """Sample sheet for ENCODE scATAC-seq data."""

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index: int) -> ENCODEScATACSeqSample:
        return self.root[index]

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "ENCODEScATACSeqSampleSheet":
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
                        samples.append(ENCODEScATACSeqSample.model_validate(row))
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

    @staticmethod
    def _validate_consistent_values(
        experiment_accession: str,
        samples: list[ENCODEScATACSeqSample],
        attr: str,
    ) -> None:
        values = {getattr(sample, attr) for sample in samples}
        if len(values) > 1:
            formatted_values = ", ".join(sorted(str(value) for value in values))
            raise ValueError(
                f"Inconsistent {attr!r} values for ENCODE experiment "
                f"{experiment_accession!r}: {formatted_values}"
            )

    @classmethod
    def _to_runs(
        cls,
        experiment_accession: str,
        samples: list[ENCODEScATACSeqSample],
    ) -> ENCODEScATACRuns:
        index_rows: dict[str, ENCODEScATACSeqSample] = {}
        read_rows_by_index: dict[str, dict[int, ENCODEScATACSeqSample]] = (
            defaultdict(dict)
        )

        for sample in samples:
            if sample.file_output_type == ENCODEFileOutputType.index_reads:
                if sample.file_accession in index_rows:
                    raise ValueError(
                        f"Duplicate index reads file {sample.file_accession!r} "
                        f"in ENCODE experiment {experiment_accession!r}"
                    )
                if sample.file_paired_end is not None:
                    raise ValueError(
                        f"Index reads file {sample.file_accession!r} in "
                        f"ENCODE experiment {experiment_accession!r} has a "
                        "'file.paired_end' value"
                    )
                if sample.file_index is not None:
                    raise ValueError(
                        f"Index reads file {sample.file_accession!r} in "
                        f"ENCODE experiment {experiment_accession!r} has a "
                        "'file.index' value"
                    )
                index_rows[sample.file_accession] = sample
                continue

            if sample.file_index is None:
                raise ValueError(
                    f"Reads file {sample.file_accession!r} in ENCODE "
                    f"experiment {experiment_accession!r} is missing "
                    "'file.index'"
                )
            if sample.file_paired_end is None:
                raise ValueError(
                    f"Reads file {sample.file_accession!r} in ENCODE "
                    f"experiment {experiment_accession!r} is missing "
                    "'file.paired_end'"
                )

            paired_reads = read_rows_by_index[sample.file_index]
            if sample.file_paired_end in paired_reads:
                raise ValueError(
                    f"Duplicate read {sample.file_paired_end} for index "
                    f"{sample.file_index!r} in ENCODE experiment "
                    f"{experiment_accession!r}"
                )
            paired_reads[sample.file_paired_end] = sample

        unknown_indexes = set(read_rows_by_index) - set(index_rows)
        if unknown_indexes:
            formatted_indexes = ", ".join(sorted(unknown_indexes))
            raise ValueError(
                f"Reads in ENCODE experiment {experiment_accession!r} refer "
                f"to missing index reads files: {formatted_indexes}"
            )

        unused_indexes = set(index_rows) - set(read_rows_by_index)
        if unused_indexes:
            formatted_indexes = ", ".join(sorted(unused_indexes))
            raise ValueError(
                f"Index reads files in ENCODE experiment "
                f"{experiment_accession!r} have no paired reads: "
                f"{formatted_indexes}"
            )

        runs = []
        for run_index, (index_accession, index_sample) in enumerate(
            index_rows.items(),
            start=1,
        ):
            paired_reads = read_rows_by_index[index_accession]
            missing_reads = {1, 2} - set(paired_reads)
            if missing_reads:
                formatted_reads = ", ".join(
                    f"read{read_number}" for read_number in sorted(missing_reads)
                )
                raise ValueError(
                    f"Index reads file {index_accession!r} in ENCODE "
                    f"experiment {experiment_accession!r} is missing "
                    f"{formatted_reads}"
                )

            runs.append(
                ENCODEScATACRun(
                    accession=f"{experiment_accession}-{run_index}",
                    read1_reads_url=paired_reads[1].file_url,
                    read2_reads_url=paired_reads[2].file_url,
                    index_reads_url=index_sample.file_url,
                    fastq_bytes=(
                        int(paired_reads[1].fastq_bytes)
                        + int(paired_reads[2].fastq_bytes)
                        + int(index_sample.fastq_bytes)
                    ),
                )
            )

        return ENCODEScATACRuns(runs)

    def to_sc_atac_seq_tasks(self) -> list[ENCODEScATACSeqTask]:
        groups: dict[str, list[ENCODEScATACSeqSample]] = defaultdict(list)
        for sample in self:
            groups[sample.experiment_accession].append(sample)

        tasks = []
        consistent_attrs = [
            "series_accession",
            "assembly_name",
            "bowtie2_index_path",
            "bowtie2_index_basename",
            "bowtie2_index_size",
            "inclusion_list",
            "output_prefix",
        ]

        for experiment_accession, samples in groups.items():
            rep = samples[0]
            for attr in consistent_attrs:
                self._validate_consistent_values(
                    experiment_accession,
                    samples,
                    attr,
                )

            tasks.append(
                ENCODEScATACSeqTask(
                    series_accession=rep.series_accession,
                    experiment_accession=rep.experiment_accession,
                    runs=self._to_runs(
                        experiment_accession,
                        samples,
                    ),
                    run_mode=RunMode.single_cell,
                    inclusion_list=rep.inclusion_list,
                    bowtie2_index=Bowtie2IndexParameter(
                        path=rep.bowtie2_index_path,
                        basename=rep.bowtie2_index_basename,
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

