import csv
import json
from pathlib import Path # Platform-independent filesystem paths


from pydantic import (
    BaseModel,
    ByteSize,
    RootModel,
    Field,
    ValidationError,
)


class MultiomeTask(BaseModel):
    total_read_files_size: ByteSize = Field(
        ...,
        description="Total size in bytes of input data. Used to size PVCs.",
    )

    rna_input_dir_s3_key: str = Field(
        ...,
        description="S3 prefix containing RNA matrix files.",
    )

    fragments_input_s3_key: str = Field(
        ...,
        description="S3 path to fragments_merged.sort.bed.gz.",
    )

    fragment_index_input_s3_key: str = Field(
        ...,
        description="S3 path to the .tbi index for the fragments file.",
    )

    peaks_input_s3_key: str = Field(
        ...,
        description="S3 path to narrowPeak file.",
    )

    gex_inclusion_s3_key: str = Field(
        ...,
        description="S3 path to GEX inclusion barcode list (737K reference).",
    )

    atac_inclusion_s3_key: str = Field(
        ...,
        description="S3 path to ATAC inclusion barcode list (737K reference).",
    )

    s3_output_key_prefix: str = Field(
            ...,
            description="Output file prefix (S3 path)",
    )

    def to_wf_parameters(self) -> dict[str, str]:
        return {
            "total_read_files_size": str(self.total_read_files_size),
            "rna_input_dir_s3_key": self.rna_input_dir_s3_key,
            "fragments_input_s3_key": self.fragments_input_s3_key,
            "fragment_index_input_s3_key": self.fragment_index_input_s3_key,
            "peaks_input_s3_key": self.peaks_input_s3_key,
            "gex_inclusion_s3_key": self.gex_inclusion_s3_key,
            "atac_inclusion_s3_key": self.atac_inclusion_s3_key,
            "s3_output_key_prefix": self.s3_output_key_prefix,

        }

class MultiomeSample(BaseModel):
    total_read_files_size: ByteSize
    rna_input_dir_s3_key: str
    fragments_input_s3_key: str
    fragment_index_input_s3_key: str
    peaks_input_s3_key: str
    gex_inclusion_s3_key: str
    atac_inclusion_s3_key: str
    s3_output_key_prefix: str

    def to_task(self) -> MultiomeTask:
        return MultiomeTask(**self.model_dump())

class MultiomeSampleSheet(
    RootModel[list[MultiomeSample]]
):
    """Collection of multiome sample-sheet rows."""

    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(
        self,
        index: int,
    ) -> MultiomeSample:
        return self.root[index]

    @classmethod
    def from_csv(
        cls,
        csv_path: Path | str,
    ) -> "MultiomeSampleSheet":

        # Normalise string paths to Path objects.
        csv_path = Path(csv_path)

        if not csv_path.exists():
            raise ValueError(
                f"CSV file not found: {csv_path}"
            )

        samples = []

        # Collect validation errors by CSV row number.
        errors: dict[int, ValidationError] = {}

        try:
            with csv_path.open(newline="") as f:
                # Header is row 1, so data rows start at row 2.
                for row_num, row in enumerate(
                    csv.DictReader(f),
                    start=2,
                ):
                    # Treat empty CSV cells as missing values.
                    row = {
                        k: (v if v != "" else None)
                        for k, v in row.items()
                    }

                    try:
                        samples.append(
                            MultiomeSample.model_validate(row)
                        )
                    except ValidationError as e:
                        errors[row_num] = e

        except OSError as e:
            raise ValueError(
                f"Failed to read CSV '{csv_path}': {e}"
            ) from e

        # Report all invalid rows together rather than
        # failing on the first one.
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

    def to_multiome_tasks(
        self,
    ) -> list[MultiomeTask]:
        """Convert each sample-sheet row into a workflow task."""

        return [
            MultiomeTask(
                total_read_files_size=(
                    sample.total_read_files_size
                ),
                rna_input_dir_s3_key=(
                    sample.rna_input_dir_s3_key
                ),
                fragments_input_s3_key=(
                    sample.fragments_input_s3_key
                ),
                fragment_index_input_s3_key=(
                    sample.fragment_index_input_s3_key
                ),
                peaks_input_s3_key=(
                    sample.peaks_input_s3_key
                ),
                gex_inclusion_s3_key=(
                    sample.gex_inclusion_s3_key
                ),
                atac_inclusion_s3_key=(
                    sample.atac_inclusion_s3_key
                ),
                s3_output_key_prefix=(
                    sample.s3_output_key_prefix
                )
            )
            for sample in self
        ]

    def to_json(
        self,
        path: Path | str,
    ) -> None:
        # Convert sample-sheet rows into workflow tasks.
        tasks = self.to_multiome_tasks()

        # Serialise each task to workflow parameters.
        json_data = [
            task.to_wf_parameters()
            for task in tasks
        ]

        Path(path).write_text(
            json.dumps(json_data, indent=4)
        )