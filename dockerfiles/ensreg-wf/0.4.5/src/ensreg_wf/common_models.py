
## To do: Improve type annotations with Gt, url, bytes, pattern, etc.

## Imports
from enum import Enum
from typing import Annotated

from pydantic import (
    BaseModel,
    ByteSize,
    Field,
    RootModel,
)

## Classes

# ENA experiment accession: ERX/DRX/SRX followed by at least 6 digits.
ENAExperimentAccession = Annotated[
    str,
    Field(pattern=r"^(E|D|S)RX[0-9]{6,}$"),
]

# ENA run accession: ERR/DRR/SRR followed by at least 6 digits.
ENARunAccession = Annotated[
    str,
    Field(pattern=r"^(E|D|S)RR[0-9]{6,}$"),
]

# Identifies the provider and version of the gene annotation dataset.
class GeneAnnotationParameter(BaseModel):
    provider: str
    version: str

# Describes the location and storage size of a STAR genome index.
## Used for both RNA Wfs
class StarIndexParameter(BaseModel):
    path: str
    size: ByteSize

# Allowed sequencing run modes.
## Used for both RNA Wfs
class RunMode(str, Enum):
    single_cell = "single-cell"
    paired_end = "paired-end"
    single_end = "single-end"

# Metadata for a paired-end ENA run, containing both read files.
class ENAPairedRun(BaseModel):
    accession: ENARunAccession
    read1_reads_url: str
    read1_file_size: int
    read1_md5: str | None
    read2_reads_url: str
    read2_file_size: int
    read2_md5: str | None

# Metadata for a single-end ENA run, containing one read file.
class ENASingleRun(BaseModel):
    accession: ENARunAccession
    read1_reads_url: str
    read1_file_size: int
    read1_md5: str | None

# Collection of ENA runs, where each run may be paired-end or single-end.
class ENARuns(
    RootModel[list[ENAPairedRun | ENASingleRun]]
):
    pass