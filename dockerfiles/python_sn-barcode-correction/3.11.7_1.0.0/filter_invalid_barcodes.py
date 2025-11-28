"""
Parallel FASTQ filtering script for snATAC-seq data
Filters R1, R2, R3 files simultaneously removing reads with invalid barcodes
detected using the barcodes_processing_v3.py script
"""

## -- Imports --


import argparse
from multiprocessing import Pool

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
    parser.add_argument('--processes', type=int, default=24, help='Number of processes (default: 8)')
    parser.add_argument("-s", "--chunk_size", type=int, default=100000, help="Number of reads per chunk for parallel processing (default = 100000)")

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

## -- Process reads chunk --
def process_chunk(chunk_data):
    """Filter invalid barcodes per reads chunk."""
    r1_chunk, r2_chunk, r3_chunk, invalid_barcodes = chunk_data
    out_r1, out_r2, out_r3 = [], [], []
    for i in range(0, len(r2_chunk), 4):
        bc_read_name = r2_chunk[i].strip().split()[0][1:]  # remove '@'
        if bc_read_name in invalid_barcodes:
            continue
        out_r1.extend(r1_chunk[i:i + 4])
        out_r2.extend(r2_chunk[i:i + 4])
        out_r3.extend(r3_chunk[i:i + 4])
    return out_r1, out_r2, out_r3

if __name__ == "__main__":
    args = parse_args()
    r1_in = args.r1
    r2_in = args.r2
    r3_in = args.r3
    invalid_bc_f = args.unmatched
    r1_out = args.out_r1
    r2_out = args.out_r2
    r3_out = args.out_r3
    processes = args.processes
    chunk_size = args.chunk_size
    chunk_lines = chunk_size * 4
    # load invalid barcodes to be removed
    invalid_bc = load_excluded_reads(invalid_bc_f)
    # creating parallel processeses
    pool = Pool(processes = processes)
    # open in and out files and process them in chunks
    with open(r1_in) as r1_f, open(r2_in) as r2_f, open(r3_in) as r3_f, \
        open(r1_out, "w") as out1, open(r2_out, "w") as out2, open(r3_out, "w") as out3:
        lines_per_chunk = chunk_size * 4 # is a fastq file
        while True:
            r1_chunk = [r1_f.readline() for _ in range(lines_per_chunk)]
            r2_chunk = [r2_f.readline() for _ in range(lines_per_chunk)]
            r3_chunk = [r3_f.readline() for _ in range(lines_per_chunk)]
            # remove potential empty strings at the end of the file
            r1_chunk = [l for l in r1_chunk if l]
            r2_chunk = [l for l in r2_chunk if l]
            r3_chunk = [l for l in r3_chunk if l]
            if not r1_chunk or not r2_chunk or not r3_chunk:
                break
            # check each chunk contains 4 rows per read
            if len(r1_chunk) % 4 != 0 or len(r2_chunk) % 4 != 0 or len(r3_chunk) % 4 != 0:
                print("Incomplete chunk at the end of the file. Ignored")
                break
            # chunk processing
            for r1_filtered, r2_filtered, r3_filtered in pool.imap(
                process_chunk, [(r1_chunk, r2_chunk, r3_chunk, invalid_bc)]):
                out1.writelines(r1_filtered)
                out2.writelines(r2_filtered)
                out3.writelines(r3_filtered)

    pool.close()
    pool.join()
