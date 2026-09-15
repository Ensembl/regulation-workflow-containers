import csv
import os
from enum import Enum
from pathlib import Path

import logfire
import typer

from .bulkrna_models import BulkRNASeqSampleSheet
from .multiome_models import MultiomeSampleSheet
from .pseudobulk_models import PseudobulkPeakCallingSampleSheet
from .scatac_models import (
    ENAScATACSeqSampleSheet,
    ENCODEScATACSeqSampleSheet,
)
from .scrna_models import ScRNASeqSampleSheet


app = typer.Typer()

@app.callback()
def cli() -> None:
    """Parse sample sheets for ENCODE workflow payloads."""

# Sample-sheet/workflow types supported by the CLI.
class SampleSheetType(str, Enum):
    SCATAC_SEQ = "sc-atac-seq"
    PSEUDOBULK_PEAK_CALLING = "pseudobulk-peak-calling"
    SCRNA_SEQ = "sc-rna-seq"
    BULK_RNA_SEQ = "bulk-rna-seq"
    MULTIOME = "multiome"


ENCODE_SCATAC_SEQ_MARKER_COLUMNS = frozenset(
    {"file.accession", "file.output_type", "file.url"}
)
ENA_SCATAC_SEQ_MARKER_COLUMNS = frozenset({"run_accession"})

# Read CSV column names for sample-sheet type detection.
def _read_csv_headers(sample_sheet: Path) -> set[str]:
    if not sample_sheet.exists():
        raise ValueError(f"CSV file not found: {sample_sheet}")

    try:
        with sample_sheet.open(newline="") as f:
            return set(csv.DictReader(f).fieldnames or [])
    except OSError as e:
        raise ValueError(f"Failed to read CSV '{sample_sheet}': {e}") from e


def _parse_scatac_seq_sample_sheet(
    sample_sheet: Path,
) -> ENAScATACSeqSampleSheet | ENCODEScATACSeqSampleSheet:
    headers = _read_csv_headers(sample_sheet)
    is_encode = ENCODE_SCATAC_SEQ_MARKER_COLUMNS <= headers
    is_ena = ENA_SCATAC_SEQ_MARKER_COLUMNS <= headers

    if is_encode and is_ena:
        raise ValueError(
            "Ambiguous sc-atac-seq sample sheet: contains both ENCODE and "
            "ENA/SRA marker columns"
        )

    if is_encode:
        return ENCODEScATACSeqSampleSheet.from_csv(sample_sheet)

    if is_ena:
        return ENAScATACSeqSampleSheet.from_csv(sample_sheet)

    raise ValueError(
        "Could not determine sc-atac-seq sample sheet source. Expected ENCODE "
        "columns like 'file.accession', 'file.output_type', 'file.url' or "
        "ENA/SRA columns like 'run_accession', 'fastq_bytes'."
    )


def _parse_scrna_seq_sample_sheet(sample_sheet: Path) -> ScRNASeqSampleSheet:
    return ScRNASeqSampleSheet.from_csv(sample_sheet)


def _parse_pseudobulk_peak_calling_sample_sheet(
    sample_sheet: Path,
) -> PseudobulkPeakCallingSampleSheet:
    return PseudobulkPeakCallingSampleSheet.from_csv(sample_sheet)


def _parse_bulk_rna_seq_sample_sheet(
    sample_sheet: Path
) -> BulkRNASeqSampleSheet:
    return BulkRNASeqSampleSheet.from_csv(sample_sheet)

def _parse_multiome_sample_sheet(sample_sheet: Path) -> MultiomeSampleSheet:
    return MultiomeSampleSheet.from_csv(sample_sheet)

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
        case SampleSheetType.PSEUDOBULK_PEAK_CALLING:
            sample_sheet = _parse_pseudobulk_peak_calling_sample_sheet(
                sample_sheet_file
            )
        case SampleSheetType.SCRNA_SEQ:
            sample_sheet = _parse_scrna_seq_sample_sheet(sample_sheet_file)
        case SampleSheetType.BULK_RNA_SEQ:
            sample_sheet = _parse_bulk_rna_seq_sample_sheet(sample_sheet_file)
        case SampleSheetType.MULTIOME:
            sample_sheet = _parse_multiome_sample_sheet(sample_sheet_file)
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

    # List generated files for debugging/logging.
    os.system('ls -altrh .')

    return 0
