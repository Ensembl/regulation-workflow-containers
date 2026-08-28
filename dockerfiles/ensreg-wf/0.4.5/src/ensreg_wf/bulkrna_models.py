# Imports
import csv  # Read CSV sample sheets.
import json  # Serialise workflow parameters to JSON.
from collections import defaultdict  # Group samples by experiment accession.
from pathlib import Path  # Platform-independent filesystem paths.

from pydantic import (
    BaseModel,       # Base class for validated data models.
    ByteSize,        # Parses and represents file sizes in bytes.
    ConfigDict,      # Configures Pydantic model behaviour.
    Field,           # Adds defaults, aliases, descriptions, etc. to fields.
    RootModel,       # Defines a model wrapping a single root value.
    ValidationError, # Raised when Pydantic validation fails.
    conint,          # Creates an integer type with constraints.
)

# Shared models and validated types used by the bulk RNA-seq models.
from .common_models import (
    ENAExperimentAccession,
    ENAPairedRun,
    ENARunAccession,
    ENARuns,
    ENASingleRun,
    GeneAnnotationParameter,
    RunMode,
    StarIndexParameter,
)

# Final task of the worflow - processing one ENA bulk RNA-seq experiment
class ENABulkRNASeqTask(BaseModel):
    experiment_accession: ENAExperimentAccession
    gene_annotation: GeneAnnotationParameter = Field(
        ...,
        description="Gene annotation information",
    )
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
    # Restrict STAR to between 1 and 32 threads, defaulting to 9.
    threads: conint(ge=1, le=32) = Field(
        default=9,
        description="Number of threads for STAR alignment",
    )

    def to_wf_parameters(self) -> dict:
        """Serialize to Argo workflow parameters."""
        return {
            "runs": self.runs.model_dump(),
            "run_mode": self.run_mode.value,
            "star_index_s3_key": self.star_index.path,
            "reference_file_size": str(self.star_index.size),
            "threads": str(self.threads),
            "s3_output_key_prefix": self.s3_output_key_prefix,
            "experiment_accession": self.experiment_accession,
            "gene_annotation_provider": self.gene_annotation.provider,
            "gene_annotation_version": self.gene_annotation.version,
        }

# Validated representation of one row(?) in a bulk RNA-seq sample sheet.
class ENABulkRNASeqSample(BaseModel):
    # Allow fields to be populated using either Python names or CSV column aliases.
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    assembly_name: str = Field(..., description="Genome assembly name")

    gene_annotation_provider: str = Field(
        ...,
        alias="gene_annotation.provider",
    )
    gene_annotation_version: str = Field(..., alias="gene_annotation.version")

    star_index_path: str = Field(..., alias="star_index.path")
    star_index_size: ByteSize = Field(..., alias="star_index.size")

    experiment_accession: ENAExperimentAccession
    run_accession: ENARunAccession


    read_1_url: str = Field(..., alias="read_1.url")
    read_1_bytes: ByteSize = Field(..., alias="read_1.bytes")
    read_1_md5: str | None = Field(None, alias="read_1.md5") # MD5 not needed ATM

    read_2_url: str | None = Field(None, alias="read_2.url")
    read_2_bytes: ByteSize | None = Field(None, alias="read_2.bytes")
    read_2_md5: str | None = Field(None, alias="read_2.md5")

    output_prefix: str = Field(..., description="Output file prefix (S3 path)")
    threads: conint(ge=1, le=32) = Field(default=9)


class BulkRNASeqSampleSheet(RootModel[list[ENABulkRNASeqSample]]):
    """Collection of bulk RNA-seq rows grouped into one task per experiment."""

    # Delegate len(sample_sheet) to the underlying sample list?
    def __len__(self) -> int:
        return len(self.root)

    # Allow direct iteration over samples in the sheet?
    def __iter__(self):
        return iter(self.root)

    # Allow list-style access to samples by index.
    def __getitem__(self, index: int) -> ENABulkRNASeqSample:
        return self.root[index]

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "BulkRNASeqSampleSheet":
        # Normalise string paths to Path objects
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise ValueError(f"CSV file not found: {csv_path}")

        samples = []

        # Collect validation errors by CSV row number
        errors: dict[int, ValidationError] = {}

        try:
            with csv_path.open(newline="") as f:
                # Header is row 1, so data starst at row 2
                for row_num, row in enumerate(csv.DictReader(f), start=2):

                    # Treat empty csv cells as missing values
                    row = {k: (v if v != "" else None) for k, v in row.items()}
                    try:
                        # Validate and conver the csv row into the sample model
                        samples.append(ENABulkRNASeqSample.model_validate(row))
                    except ValidationError as e:
                        errors[row_num] = e
        except OSError as e:
            raise ValueError(f"Failed to read CSV '{csv_path}': {e}") from e

        # Report all invalid rows together, don't just fail at the first
        if errors:
            error_summary = "\n\n".join(
                f"Row {row_num}:\n{error}" for row_num, error in errors.items()
            )
            raise ValueError(
                f"Sample sheet validation failed:\n\n{error_summary}"
            )

        return cls(samples)

    # Ensure all rows for an experiment use the same value for the given field
    @staticmethod
    def _validate_consistent_values(
        experiment_accession: str,
        samples: list[ENABulkRNASeqSample],
        attr: str,
    ) -> None:
        values = {getattr(sample, attr) for sample in samples}
        if len(values) > 1:
            formatted_values = ", ".join(sorted(str(value) for value in values))
            raise ValueError(
                f"Inconsistent {attr!r} values for bulk RNA-seq experiment "
                f"{experiment_accession!r}: {formatted_values}"
            )

    # Check whether a sample contains any second-read metadata.
    ##  should we be adding m5d here? 
    @staticmethod
    def _has_read_2(sample: ENABulkRNASeqSample) -> bool:
        return sample.read_2_url is not None or sample.read_2_bytes is not None

    def to_bulk_rna_seq_tasks(self) -> list[ENABulkRNASeqTask]:
        # Group sample-sheet rows by ENA experiment accession.
        groups: dict[str, list[ENABulkRNASeqSample]] = defaultdict(list)
        for sample in self:
            groups[sample.experiment_accession].append(sample)

        tasks = []

        # Fields that must be identical across all runs in an experiment.
        consistent_attrs = (
            "assembly_name",
            "gene_annotation_provider",
            "gene_annotation_version",
            "star_index_path",
            "star_index_size",
            "output_prefix",
            "threads",
        )

        for experiment_accession, samples in groups.items():
            # Use the first row as the representative for experiment-level values.
            rep = samples[0]
            # Validate experiment-level fields before combining the rows.
            for attr in consistent_attrs:
                self._validate_consistent_values(
                    experiment_accession,
                    samples,
                    attr,
                )

            # Convert each sample-sheet row into a paired- or single-end ENA run.
            runs: list[ENAPairedRun | ENASingleRun] = []
            for sample in samples:
                if self._has_read_2(sample):
                    if sample.read_2_url is None or sample.read_2_bytes is None:
                        raise ValueError(
                            f"Run {sample.run_accession!r} in bulk RNA-seq "
                            f"experiment {experiment_accession!r} has incomplete "
                            "read_2 fields"
                        ) # Paired-end runs require both the read-2 URL and file size.

                    runs.append(
                        ENAPairedRun(
                            accession=sample.run_accession,
                            read1_reads_url=sample.read_1_url,
                            read1_file_size=int(sample.read_1_bytes),
                            read1_md5=sample.read_1_md5,
                            read2_reads_url=sample.read_2_url,
                            read2_file_size=int(sample.read_2_bytes),
                            read2_md5=sample.read_2_md5,
                        )
                    )
                else:
                    runs.append(
                        ENASingleRun(
                            accession=sample.run_accession,
                            read1_reads_url=sample.read_1_url,
                            read1_file_size=int(sample.read_1_bytes),
                            read1_md5=sample.read_1_md5,
                        )
                    )

            run_types = {type(run) for run in runs}
            if len(run_types) > 1:
                raise ValueError(
                    f"Mixed paired/single-end runs in experiment "
                    f"{experiment_accession!r}"
                ) # Do not allow paired-end and single-end runs in the same experiment.

            # Set the experiment run mode from the validated run type.
            ## TO CHECK! So we're not adding this in the sample sheet?
            run_mode = (
                RunMode.paired_end
                if run_types == {ENAPairedRun}
                else RunMode.single_end
            )

            # Combine experiment-level metadata and runs into one workflow task
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
                    experiment_accession=rep.experiment_accession,
                    gene_annotation=GeneAnnotationParameter(
                        provider=rep.gene_annotation_provider,
                        version=rep.gene_annotation_version,
                    ),
                )
            )

        return tasks

    def to_json(self, path: Path | str) -> None:
        # Convert sample-sheet rows into workflow tasks.
        tasks = self.to_bulk_rna_seq_tasks()

        # Serialize each task to Argo workflow parameters.
        json_data = [task.to_wf_parameters() for task in tasks]

        # Write formatted workflow parameters to JSON.
        Path(path).write_text(json.dumps(json_data, indent=4))
