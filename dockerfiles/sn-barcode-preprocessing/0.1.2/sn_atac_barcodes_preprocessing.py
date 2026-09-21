"""
When needed, remove offset and reverse-complement
snATAC-seq barcodes by comparing with the inclusion list.

Exit codes:
    0  barcodes processed, output file written
    1  unexpected error (unreadable/truncated input, empty input, compression failure, ...)
    2  invalid command-line arguments
    3  barcodes don't match the inclusion list in either orientation; no output file written
"""

## -- Imports --
import os
import io
import sys
import gzip
import signal
import argparse
import subprocess
from contextlib import contextmanager
from Bio.SeqIO.QualityIO import FastqGeneralIterator

EXIT_BARCODES_MISMATCH = 3

## -- Arguments parser --
def parse_args():
    parser = argparse.ArgumentParser(description="Remove barcodes offset, and reverse and complement if required, for snATAC-seq experiments")
    parser.add_argument("-f", "--fastq", required=True,
                        help="Path to FASTQ/FASTQ.GZ file containing the barcode reads")
    parser.add_argument("-w", "--inclusion_list", required=True,
                        help="Path to the inclusion_list file")
    parser.add_argument("-o", "--out_file", required=True,
                        help="Path to the output FASTQ/FASTQ.GZ file")
    parser.add_argument("-t", "--offset", type=int, default=0,
                        help="Number of bases after which the barcode starts in the read")
    parser.add_argument("-n", "--sample_size", type=int, default=500000,
                        help="Size of the random sample of barcodes for determining their orientation (default = 500000)")
    parser.add_argument("-d", "--min_prop_dir", type=float, default=0.6,
                        help="Minimum proportion for deciding barcode orientation (default = 0.6)")
    parser.add_argument('--cores', type=int, default=4,
                        help='Number of cores for pigz (default: 4)')
    parser.add_argument('--no-pigz', dest='use_pigz', action='store_false',
                        help='Disable pigz, fall back to gzip')
    parser.set_defaults(use_pigz=True)
    return parser.parse_args()

#############
## Helpers ##
#############

@contextmanager
def open_file(path, use_pigz, cores, mode='rt'):
    """Open a plain or gzipped file, using pigz when requested. Raises if pigz fails."""
    if not (path.endswith('.gz') and use_pigz):
        with (gzip.open(path, mode) if path.endswith('.gz') else open(path, mode)) as handle:
            yield handle
        return
    if 'r' in mode:
        proc = subprocess.Popen(
            ['pigz', '-d', '-c', f'-p{cores}', path],
            stdout=subprocess.PIPE
        )
        handle = io.TextIOWrapper(proc.stdout, encoding='utf-8')
        try:
            yield handle
        finally:
            handle.close()
            returncode = proc.wait()
        # SIGPIPE only means the caller stopped reading early (e.g. sampling), not a bad file
        if returncode not in (0, -signal.SIGPIPE):
            raise RuntimeError(f"pigz failed to decompress {path} (exit code {returncode})")
    else:
        with open(path, 'wb') as out_f:
            proc = subprocess.Popen(
                ['pigz', '-c', f'-p{cores}'],
                stdin=subprocess.PIPE,
                stdout=out_f
            )
            handle = io.TextIOWrapper(proc.stdin, encoding='utf-8')
            try:
                yield handle
            finally:
                handle.close()
                # Wait for pigz to flush everything before the file is considered done
                returncode = proc.wait()
        if returncode != 0:
            raise RuntimeError(f"pigz failed to compress {path} (exit code {returncode})")

## -- Reverse and complement --
def reverse_complement(seq):
    """Reverse and complement a DNA sequence"""
    comp = str.maketrans("ACGT", "TGCA")
    return seq.translate(comp)[::-1]

## -- Barcode direction detection --
def barcodes_match(fastq_file, inclusion_list,sample_size,offset, thresh,use_pigz, cores):
    """Identify barcode orientation and report if reverse and complement operation is needed"""
    rc_inclusion_list = {reverse_complement(bc) for bc in inclusion_list}
    bc_match = 0
    bcrc_match = 0
    with open_file(fastq_file, use_pigz, cores,"rt") as handle:
        bc_sample = []
        for record in fastq_iter(handle):
            bc_sample.append(record)
            if len(bc_sample) >= sample_size:
                break
    sample_size = min(sample_size, len(bc_sample))
    if sample_size == 0:
        raise RuntimeError(f"No reads found in {fastq_file}")
    for title, bc, plus, qual in bc_sample:
        if bc.split()[0][offset:] in inclusion_list:
            bc_match += 1
        if bc.split()[0][offset:] in rc_inclusion_list:
            bcrc_match += 1
    bc_match_prop = bc_match / sample_size
    bcrc_match_prop = bcrc_match / sample_size
    valid = (bc_match_prop >= thresh) or (bcrc_match_prop >= thresh)
    rc_need = (bcrc_match_prop >= bc_match_prop)
    print(f"Direct match proportion: {bc_match_prop}\n")
    print(f"Reverse-complement match proportion: {bcrc_match_prop}\n")
    if valid:
        print(f"Reverse-complement required: {rc_need}\n")
    else:
        print(f"The barcodes don't match the inclusion list: direct {bc_match_prop:.4f}, "
              f"reverse-complement {bcrc_match_prop:.4f}, minimum {thresh} "
              f"(sample of {sample_size} reads, offset {offset})", file=sys.stderr)
        rc_need = None
    return(rc_need)
## -- Define fastq iterator --
def fastq_iter(handle):
    while True:
        h = handle.readline()
        if not h:
            return
        s = handle.readline()
        p = handle.readline()
        q = handle.readline()
        yield h, s, p, q

## ----------- main --------- ##

if __name__ == "__main__":
    args = parse_args()
    fastq_file = args.fastq
    inclusion_list_file = args.inclusion_list
    corrected_file = args.out_file
    offset = args.offset
    num_cores = args.cores
    sample_size = args.sample_size
    min_prop_dir = args.min_prop_dir
    use_pigz = args.use_pigz

    # loading inclusion_list
    with open_file(inclusion_list_file,  use_pigz, num_cores,  "rt") as f:
        inclusion_list = [line.strip() for line in f if line.strip()]

    # determine if reverse and complement operation is needed
    rc_need = barcodes_match(fastq_file, set(inclusion_list), sample_size, offset, min_prop_dir,  use_pigz, num_cores )
    if rc_need is None:
        sys.exit(EXIT_BARCODES_MISMATCH)
    print("Barcodes reverse and complement status:", rc_need)

    # processing: write to a hidden partial file and rename it only once complete,
    # so a failure never leaves a truncated output under the final name
    out_dir, out_name = os.path.split(corrected_file)
    partial_file = os.path.join(out_dir, f".{out_name}.partial{os.path.splitext(out_name)[1]}")
    try:
        with open_file(fastq_file, use_pigz, num_cores,  "rt") as barcodes_in, open_file(partial_file, use_pigz, num_cores, "wt") as barcodes_out:
            for bc_rec in fastq_iter(barcodes_in):
                bc_rec = list(bc_rec)
                bc_seq = bc_rec[1].split()[0][offset:]
                bc_qual = bc_rec[3].split()[0][offset:]  # selecting barcode read quality
                if rc_need:
                    bc_seq = reverse_complement(bc_seq)
                    bc_qual = bc_qual[::-1]
                bc_rec[1] = bc_seq +'\n'
                bc_rec[3] = bc_qual +'\n'
                barcodes_out.writelines(bc_rec)
    except BaseException:
        if os.path.exists(partial_file):
            os.remove(partial_file)
        raise
    os.replace(partial_file, corrected_file)
