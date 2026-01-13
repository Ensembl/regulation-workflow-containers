"""
FASTQ filtering script for snATAC-seq data
Filters R1, R2, R3 files simultaneously removing reads with invalid barcodes
detected using the barcodes_processing_v3.py script
"""

## -- Imports --
import argparse

## -- Arguments parser --
def parse_args():
    parser = argparse.ArgumentParser(description='Filter FASTQ files based on barcode whitelist')
    parser.add_argument('--r1', required=True, help='R1 FASTQ file (reads)')
    parser.add_argument('--r2', required=True, help='R2 FASTQ file (corrected barcodes)')
    parser.add_argument('--r3', required=True, help='R3 FASTQ file (reads)')
    parser.add_argument('--unmatched', required=True, help='Text file with unmatched barcodes')
    parser.add_argument('--out_r1', required=True, help='Filtered R1 FASTQ file (reads))')
    parser.add_argument('--out_r2', required=True, help='Filtered R2 FASTQ file (corrected barcodes)')
    parser.add_argument('--out_r3', required=True, help='Filtered R3 FASTQ file (reads))')
    return parser.parse_args()

## -- Load uncorrected reads --
def load_excluded_reads(unmatched_file):
    """Load read names to exclude from unmatched_barcodes.txt"""
    excluded_reads = set() 
    with open(unmatched_file, 'r') as f:
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
    r3_in = args.r3
    invalid_bc_f = args.unmatched
    r1_out = args.out_r1
    r2_out = args.out_r2
    r3_out = args.out_r3
    
    # load invalid barcodes to be removed
    invalid_bc = load_excluded_reads(invalid_bc_f)
    kept_bc = 0
    skipped_bc = 0

    # processing 
    with open(r1_in) as r1_f, open(r2_in) as r2_f, open(r3_in) as r3_f, \
        open(r1_out, "w") as out1, open(r2_out, "w") as out2, open(r3_out, "w") as out3:
        for r1_rec, r2_rec, r3_rec in zip(fastq_iter(r1_f), fastq_iter(r2_f), fastq_iter(r3_f)):
            name = r2_rec[0][1:].split()[0]
            if name in invalid_bc:
                skipped_bc += 1
                continue
            out1.writelines(r1_rec)
            out2.writelines(r2_rec)
            out3.writelines(r3_rec)
            kept_bc += 1
    print(f"Kept reads: {kept_bc}")
    print(f"Removed reads: {skipped_bc}")
