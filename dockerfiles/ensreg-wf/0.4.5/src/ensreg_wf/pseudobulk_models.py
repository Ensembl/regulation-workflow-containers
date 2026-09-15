import csv
import json
from collections import defaultdict
from pathlib import Path

from pydantic import (
    BaseModel,
    ByteSize,
    Field,
    RootModel,
    ValidationError,
)


class PseudobulkPeakCallingSample(BaseModel):
    """One aligned BAM contributing to a pseudobulk peak-calling task."""

    experiment_name: str
    alignment_file_name: str = Field(
        ...,
        pattern=r"^.+\.bam$",
        description="Aligned BAM filename, including the .bam suffix",
    )
    alignment_file_size: ByteSize
    s3_path_alignment_folder: str
    s3_path_peaks_folder: str
    masked_regions_s3_key: str | None = None
    masked_regions_filename: str | None = None
    intermediate_peaks: bool = False


class PseudobulkPeakCallingTask(BaseModel):
    """Payload consumed by the pseudobulk peak-calling Argo workflow."""

    experiment_name: str
    signals: list[dict[str, str]]
    alignment_files_total_size: int
    masked_regions_s3_key: str = ""
    masked_regions_filename: str = ""
    s3_path_peaks_folder: str
    intermediate_peaks: bool = False

    def to_wf_parameters(self) -> dict:
        return {
            "experiment_name": self.experiment_name,
            "alignments_info": {"signals": self.signals},
            "alignment_files_total_size": self.alignment_files_total_size,
            "masked_regions_s3_key": self.masked_regions_s3_key,
            "masked_regions_filename": self.masked_regions_filename,
            "s3_path_peaks_folder": self.s3_path_peaks_folder,
            "intermediate_peaks": str(self.intermediate_peaks).lower(),
        }


class PseudobulkPeakCallingSampleSheet(
    RootModel[list[PseudobulkPeakCallingSample]]
):
    """Sample sheet for pseudobulk ATAC-seq peak calling.

    Rows are individual aligned BAM files. Rows sharing an ``experiment_name``
    are combined into one peak-calling task.
    """

    def __len__(self) -> int:
        return len({sample.experiment_name for sample in self.root})

    def __iter__(self):
        return iter(self.root)

    @classmethod
    def from_csv(cls, csv_path: Path | str) -> "PseudobulkPeakCallingSampleSheet":
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
                        samples.append(PseudobulkPeakCallingSample.model_validate(row))
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

    def to_pseudobulk_peak_calling_tasks(self) -> list[PseudobulkPeakCallingTask]:
        groups: dict[str, list[PseudobulkPeakCallingSample]] = defaultdict(list)
        for sample in self:
            groups[sample.experiment_name].append(sample)

        tasks = []
        for experiment_name, samples in groups.items():
            representative = samples[0]

            if not representative.s3_path_peaks_folder.endswith("/"):
                raise ValueError(
                    f"Experiment '{experiment_name}': s3_path_peaks_folder must end "
                    "with '/'."
                )

            expected_task_fields = (
                "s3_path_peaks_folder",
                "masked_regions_s3_key",
                "masked_regions_filename",
                "intermediate_peaks",
            )
            for sample in samples[1:]:
                for field_name in expected_task_fields:
                    if getattr(sample, field_name) != getattr(representative, field_name):
                        raise ValueError(
                            f"Experiment '{experiment_name}': '{field_name}' must be "
                            "identical for every row in the task."
                        )

            has_masked_regions_key = representative.masked_regions_s3_key is not None
            has_masked_regions_filename = (
                representative.masked_regions_filename is not None
            )
            if has_masked_regions_key != has_masked_regions_filename:
                raise ValueError(
                    f"Experiment '{experiment_name}': masked_regions_s3_key and "
                    "masked_regions_filename must either both be supplied or both be "
                    "empty."
                )

            signals = []
            seen_alignments = set()
            for sample in samples:
                if not sample.s3_path_alignment_folder.endswith("/"):
                    raise ValueError(
                        f"Experiment '{experiment_name}': s3_path_alignment_folder "
                        "must end with '/'."
                    )
                alignment_key = (
                    sample.s3_path_alignment_folder,
                    sample.alignment_file_name,
                )
                if alignment_key in seen_alignments:
                    raise ValueError(
                        f"Experiment '{experiment_name}': duplicate alignment "
                        f"'{sample.alignment_file_name}'."
                    )
                seen_alignments.add(alignment_key)
                signals.append({
                    "alignment_file_name": sample.alignment_file_name,
                    "s3_path_alignment_folder": sample.s3_path_alignment_folder,
                })

            tasks.append(
                PseudobulkPeakCallingTask(
                    experiment_name=experiment_name,
                    signals=signals,
                    alignment_files_total_size=sum(
                        int(sample.alignment_file_size) for sample in samples
                    ),
                    masked_regions_s3_key=representative.masked_regions_s3_key or "",
                    masked_regions_filename=(
                        representative.masked_regions_filename or ""
                    ),
                    s3_path_peaks_folder=representative.s3_path_peaks_folder,
                    intermediate_peaks=representative.intermediate_peaks,
                )
            )

        return tasks

    def to_json(self, path: Path | str) -> None:
        tasks = self.to_pseudobulk_peak_calling_tasks()
        Path(path).write_text(json.dumps(
            [task.to_wf_parameters() for task in tasks], indent=4
        ))

