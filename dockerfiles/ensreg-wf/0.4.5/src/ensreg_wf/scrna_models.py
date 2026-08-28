import csv
import json
from collections import defaultdict  # Group samples by experiment accession.
from pathlib import Path  # Platform-independent filesystem paths.

from pydantic import (
    BaseModel,        # Base class for validated data models.
    ByteSize,         # Parses and represents file sizes in bytes.
    ConfigDict,       # Configures Pydantic model behaviour.
    Field,            # Adds defaults, aliases, descriptions, etc. to fields.
    RootModel,        # Defines a model wrapping a single root value.
    ValidationError,  # Raised when Pydantic validation fails.
    conint,           # Creates an integer type with constraints.
)

# Shared models and validated types used by the scRNA-seq models.
from .common_models import (
    ENAExperimentAccession,
    ENAPairedRun,
    ENARunAccession,
    ENARuns,
    GeneAnnotationParameter,
    RunMode,
    StarIndexParameter,
)

# Workflow task for processing one ENA single-cell RNA-seq experiment.
class ENAScRNASeqTask(BaseModel):
    experiment_accession: ENAExperimentAccession
    gene_annotation: GeneAnnotationParameter
    runs: ENARuns

    # scRNA-seq tasks use single-cell mode by default.
    run_mode: RunMode = Field(
        default=RunMode.single_cell,
        description="Run mode for scRNA-seq",
    )

    star_index: StarIndexParameter = Field(
        ...,
        description="STAR index reference",
    )

    barcode_inclusion_s3_key: str = Field(
        ...,
        description="Path to barcode inclusion list",
    )

    s3_output_key_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path)",
    )
    # Restrict STAR to between 1 and 32 threads, defaulting to 16
    threads: conint(ge=1, le=32) = Field(
        default=16,
        description="Number of threads for STAR alignment",
    )

    def to_wf_parameters(self) -> dict[str, str]:
        # Convert the task into parameters expected by the Argo workflow
        return {
            "runs": self.runs.model_dump(), # Have I messed this one up? not sure it's a str
            "run_mode": self.run_mode.value,
            "star_index_s3_key": self.star_index.path,
            "reference_file_size": str(self.star_index.size),
            "barcode_inclusion_s3_key": self.barcode_inclusion_s3_key,
            "threads": str(self.threads),
            "s3_output_key_prefix": self.s3_output_key_prefix,
            "experiment_accession": self.experiment_accession,
            "gene_annotation_provider": self.gene_annotation.provider,
            "gene_annotation_version": self.gene_annotation.version,
        }

# Validated representation of one row in an scRNA-seq sample sheet.
class ENAScRNASeqSample(BaseModel):
    # Allow fields to be populated using either Python names or CSV column aliases.
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )

    assembly_name: str = Field(
        ...,
        description="Genome assembly name",
    )

    gene_annotation_provider: str = Field(
        ...,
        alias="gene_annotation.provider",
    )
    gene_annotation_version: str = Field(
        ...,
        alias="gene_annotation.version",
    )

    star_index_path: str = Field(
        ...,
        alias="star_index.path",
    )
    star_index_size: ByteSize = Field(
        ...,
        alias="star_index.size",
    )

    experiment_accession: ENAExperimentAccession
    run_accession: ENARunAccession

    # scRNA-seq runs require both read files and their associated metadata.
    read_1_url: str = Field(..., alias="read_1.url")
    read_1_bytes: ByteSize = Field(..., alias="read_1.bytes")
    read_1_md5: str = Field(..., alias="read_1.md5")

    read_2_url: str = Field(..., alias="read_2.url")
    read_2_bytes: ByteSize = Field(..., alias="read_2.bytes")
    read_2_md5: str = Field(..., alias="read_2.md5")

    output_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path)",
    )

    threads: conint(ge=1, le=32) = Field(default=16)

    run_mode: RunMode = Field(
        default=RunMode.single_cell,
    )

    inclusion_list: str = Field(
        ...,
        description="Path to barcode inclusion list",
    )


class ScRNASeqSampleSheet(
    RootModel[list[ENAScRNASeqSample]]
):
    """Collection of scRNA-seq rows grouped into one task per experiment."""

    # Return the number of unique experiments rather than the number of CSV rows.
    def __len__(self) -> int:
        return len({
            sample.experiment_accession
            for sample in self.root
        })

    def __iter__(self):
        return iter(self.root)

    def __getitem__(
        self,
        index: int,
    ) -> ENAScRNASeqSample:
        return self.root[index]

    @classmethod
    def from_csv(
        cls,
        csv_path: Path | str,
    ) -> "ScRNASeqSampleSheet":

        # Normalise string paths to Path objects
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise ValueError(
                f"CSV file not found: {csv_path}"
            )

        samples = []

        ## Collect validation errors by csv row numeber. 
        errors: dict[int, ValidationError] = {}

        try:
            with csv_path.open(newline="") as f:
                # Header is row 1, so data rows start at row 2.
                for row_num, row in enumerate(
                    csv.DictReader(f),
                    start=2,
                ):
                    # Treat empty CSV cells as missing values
                    row = {
                        k: (v if v != "" else None)
                        for k, v in row.items()
                    }

                    try:
                        samples.append(
                            ENAScRNASeqSample.model_validate(row)
                        )
                    except ValidationError as e:
                        errors[row_num] = e

        except OSError as e:
            raise ValueError(
                f"Failed to read CSV '{csv_path}': {e}"
            ) from e
        
        # Report all invalid rows together rather than failing on the first one.
        if errors:
            error_summary = "\n\n".join(
                f"Row {row_num}:\n{error}"
                for row_num, error in errors.items()
            )

            raise ValueError(
                "Sample sheet validation failed:"
                f"\n\n{error_summary}"
            )

        return cls(samples)

    def to_sc_rna_seq_tasks(
        self,
    ) -> list[ENAScRNASeqTask]:

        # Group sample-sheet rows by ENA experiment accession.
        groups: dict[
            str,
            list[ENAScRNASeqSample],
        ] = defaultdict(list)

        for sample in self:
            groups[
                sample.experiment_accession
            ].append(sample)

        tasks = []

        # Fields that must be identical across all runs in an experiment.
        shared_fields = (
            "assembly_name",
            "gene_annotation_provider",
            "gene_annotation_version",
            "star_index_path",
            "star_index_size",
            "output_prefix",
            "threads",
            "run_mode",
            "inclusion_list",
        )

        for experiment_accession, samples in groups.items():
            rep = samples[0]
            # Ensure experiment-level values are consistent across all runs.
            for sample in samples[1:]:
                for field_name in shared_fields:
                    if (
                        getattr(sample, field_name)
                        != getattr(rep, field_name)
                    ):
                        raise ValueError(
                            f"Inconsistent {field_name!r} "
                            "for scRNA-seq experiment "
                            f"{experiment_accession!r}"
                        )
                    
            # Convert every sample-sheet row into a paired-end ENA run.
            runs = [
                ENAPairedRun(
                    accession=sample.run_accession,
                    read1_reads_url=sample.read_1_url,
                    read1_file_size=int(
                        sample.read_1_bytes
                    ),
                    read1_md5=sample.read_1_md5,
                    read2_reads_url=sample.read_2_url,
                    read2_file_size=int(
                        sample.read_2_bytes
                    ),
                    read2_md5=sample.read_2_md5,
                )
                for sample in samples
            ]

            tasks.append(
                ENAScRNASeqTask(
                    runs=ENARuns(runs),
                    run_mode=rep.run_mode,
                    star_index=StarIndexParameter(
                        path=rep.star_index_path,
                        size=rep.star_index_size,
                    ),
                    barcode_inclusion_s3_key=(
                        rep.inclusion_list
                    ),
                    s3_output_key_prefix=(
                        rep.output_prefix
                    ),
                    threads=rep.threads,
                    experiment_accession=(
                        rep.experiment_accession
                    ),
                    gene_annotation=GeneAnnotationParameter(
                        provider=(
                            rep.gene_annotation_provider
                        ),
                        version=(
                            rep.gene_annotation_version
                        ),
                    ),
                )
            )

        return tasks

    def to_json(
        self,
        path: Path | str,
    ) -> None:
        # Convert sample-sheet rows into experiment-level workflow tasks
        tasks = self.to_sc_rna_seq_tasks()

        # Serialise each task to workflow parameters.
        json_data = [
            task.to_wf_parameters()
            for task in tasks
        ]

        Path(path).write_text(
            json.dumps(json_data, indent=4)
        )
