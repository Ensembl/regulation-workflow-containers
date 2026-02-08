import csv
import json
from pathlib import Path

import logfire
from typing import Annotated

import typer
from pydantic import (
    BaseModel,
    Field,
    ByteSize,
    conint,
    conlist,
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


class ReadFileParameter(BaseModel):
    url: str
    bytes: ByteSize
    md5: str


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
                        f"Error parsing row {row_num} (accession: {row.get('run_accession', 'unknown')}): {e}"
                    ) from e

        return cls(tasks=tasks)

    def to_json(self, file_name) -> str:
        """Serialize the sample sheet to JSON format."""
        with open(file_name, "w") as f:
            json_data = [t.to_wf_parameters() for t in self.tasks]
            json.dump(json_data, f, indent=4)


app = typer.Typer()

@app.command("parse")
@logfire.instrument("'parse' sample sheet: {sample_sheet=}")
def parse_sample_sheet(
    sample_sheet: Path = typer.Argument(..., help="Path to the sample sheet CSV file")
) -> int:

    output_json = sample_sheet.stem + ".json"

    logfire.info(f"Parsing sample sheet CSV: {sample_sheet}")

    sample_sheet = ScRNASeqSampleSheet.from_csv(sample_sheet)

    logfire.info(f"Parsed {len(sample_sheet.tasks)} tasks from sample sheet.")

    with open('num_tasks.txt', 'w') as f:
        f.write(str(len(sample_sheet.tasks)))

    print(f"Payload:\n{sample_sheet.model_dump_json(indent=4)}")

    logfire.info(f"Serializing sample sheet to JSON: {output_json}")

    sample_sheet.to_json(output_json)

    os.system('ls -altrh .')

    return 0


