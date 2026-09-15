import csv
import json
from pathlib import Path

from pydantic import (
    BaseModel,
    ByteSize,
    RootModel,
    Field,
    ValidationError,
    field_validator,
)


class MultiomeTask(BaseModel):
    unique_id: str = Field(
        ...,
        description="Unique identifier for the multiome sample.",
    )

    total_read_file_size: ByteSize = Field(
        ...,
        description="Total size in bytes of input data. Used to size PVCs.",
    )

    rna_input_dir_s3_key: str = Field(
        ...,
        description="S3 prefix containing RNA matrix files.",
    )

    fragments_input_s3_key: str = Field(
        ...,
        description="S3 path to fragments file.",
    )

    peaks_input_s3_key: str = Field(
        ...,
        description="S3 prefix/path containing peak data.",
    )

    gex_inclusion_s3_key: str = Field(
        ...,
        description="S3 path to GEX inclusion barcode list.",
    )

    atac_inclusion_s3_key: str = Field(
        ...,
        description="S3 path to ATAC inclusion barcode list.",
    )

    s3_output_key_prefix: str = Field(
        ...,
        description="Output file prefix (S3 path).",
    )

    def to_wf_parameters(self) -> dict[str, str]:
        return {
            "unique_id": self.unique_id,
            "total_read_file_size": str(self.total_read_file_size),
            "rna_input_dir_s3_key": self.rna_input_dir_s3_key,
            "fragments_input_s3_key": self.fragments_input_s3_key,
            "peaks_input_s3_key": self.peaks_input_s3_key,
            "gex_inclusion_s3_key": self.gex_inclusion_s3_key,
            "atac_inclusion_s3_key": self.atac_inclusion_s3_key,
            "s3_output_key_prefix": self.s3_output_key_prefix,
        }


class MultiomeSample(BaseModel):
    unique_id: str
    total_read_file_size: ByteSize
    rna_input_dir_s3_key: str
    fragments_input_s3_key: str
    peaks_input_s3_key: str
    gex_inclusion_s3_key: str
    atac_inclusion_s3_key: str
    s3_output_key_prefix: str

    @field_validator(
        "total_read_file_size",
        mode="before",
    )
    @classmethod
    def parse_scientific_notation_size(cls, value):
        """
        Convert values such as '1e+09' from R-generated CSVs
        into an integer number of bytes.
        """
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                # Leave values such as "1 GB" for ByteSize
                # to parse normally.
                return value

        return value

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
                reader = csv.DictReader(f)

                for row_num, row in enumerate(
                    reader,
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
            sample.to_task()
            for sample in self
        ]

    def to_json(
        self,
        path: Path | str,
    ) -> None:
        tasks = self.to_multiome_tasks()

        json_data = [
            task.to_wf_parameters()
            for task in tasks
        ]

        Path(path).write_text(
            json.dumps(json_data, indent=4)
        )