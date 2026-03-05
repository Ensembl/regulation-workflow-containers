"""
FASTQ filtering script for snATAC-seq data
Filters R1, and R2 files simultaneously removing reads with invalid barcodes
detected using the barcodes_processing.py script and attaches corrected barcodes
to read names
"""

## -- Imports --
import argparse
import gzip
## -- Arguments parser --
def parse_args():
    parser = argparse.ArgumentParser(description='Filter FASTQ files based on barcode whitelist')
    parser.add_argument('--r1', required=True, help='R1 FASTQ file (.gz)')
    parser.add_argument('--r2', required=True, help='R2 FASTQ file (.gz)')
    parser.add_argument('--corrected', required=True, help='Corrected barcodes FASTQ file (.gz)')
    parser.add_argument('--unmatched', required=True, help='Text file with unmatched barcodes')
    parser.add_argument('--out_r1', required=True, help='Filtered R1 FASTQ file (.gz)')
    parser.add_argument('--out_r2', required=True, help='Filtered R2 FASTQ file (.gz)')
    return parser.parse_args()

## -- Handle compressed and decompressed files --
def open_file(path, mode='rt'):
    return gzip.open(path, mode) if path.endswith('.gz') else open(path, mode)
    
## -- Load uncorrected reads --
def load_excluded_reads(unmatched_file):
    """Load read names to exclude from unmatched_barcodes.txt"""
    excluded_reads = set() 
    with open_file(unmatched_file, 'rt') as f:
        for line in f:
            line = line.strip()
            if line.startswith('@'):
                # Extract read name (remove '@' and everything after first space)
                read_name = line[1:].split()[0]
                excluded_reads.add(read_name)
    print(f"Loaded {len(excluded_reads)} read names to exclude")
    return excluded_reads

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

## -- Main --
if __name__ == "__main__":
    args = parse_args()
    r1_in = args.r1
    r2_in = args.r2
    bc_in = args.corrected
    invalid_bc_f = args.unmatched
    r1_out = args.out_r1
    r2_out = args.out_r2
    
    # load invalid barcodes to be removed
    invalid_bc = load_excluded_reads(invalid_bc_f)
    kept_bc = 0
    skipped_bc = 0

    # processing 
    with open_file(r1_in, "rt") as r1_f, open_file(r2_in, "rt") as r2_f, open_file(bc_in, "rt") as bc_f, \
        open_file(r1_out, "wt") as out1, open_file(r2_out, "wt") as out2:
        for r1_rec, r2_rec, bc_rec in zip(fastq_iter(r1_f), fastq_iter(r2_f), fastq_iter(bc_f)):
            name = bc_rec[0][1:].split()[0]
            if name in invalid_bc:
                skipped_bc += 1
                continue
            r1_rec = list(r1_rec)
            r1_rec[0] = '@'+bc_rec[1].split()[0]+':'+r1_rec[0][1:]
            r2_rec = list(r2_rec)
            r2_rec[0] = '@'+bc_rec[1].split()[0]+':'+r2_rec[0][1:]
            out1.writelines(r1_rec)
            out2.writelines(r2_rec)
            kept_bc += 1
    print(f"Kept reads: {kept_bc}")
    print(f"Removed reads: {skipped_bc}")
