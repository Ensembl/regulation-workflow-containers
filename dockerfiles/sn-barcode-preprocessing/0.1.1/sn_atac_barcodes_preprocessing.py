"""
When needed, remove offset and reverse-complement
snATAC-seq barcodes by comparing with the inclusion list.
"""

## -- Imports --
import os
import io
import gzip
import argparse
import subprocess
from Bio.SeqIO.QualityIO import FastqGeneralIterator

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
## Helpers ##
#############

def open_file(path, use_pigz, cores, mode='rt'):
    if path.endswith('.gz'):
        if use_pigz:
            if 'r' in mode:
                proc = subprocess.Popen(
                    ['pigz', '-d', '-c', f'-p{cores}', path],
                    stdout=subprocess.PIPE
                )
                return io.TextIOWrapper(proc.stdout, encoding='utf-8')
            else:
                out_f = open(path, 'wb')
                proc = subprocess.Popen(
                    ['pigz', '-c', f'-p{cores}'],
                    stdin=subprocess.PIPE,
                    stdout=out_f
                )
                return io.TextIOWrapper(proc.stdin, encoding='utf-8')
        return gzip.open(path, mode)
    return open(path, mode)

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
        print("The barcodes doesn't match the inclusion list")
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
        exit()
    print("Barcodes reverse and complement status:", rc_need)

    # processing 
    with open_file(fastq_file, use_pigz, num_cores,  "rt") as barcodes_in, open_file(corrected_file, use_pigz, num_cores, "wt") as barcodes_out:
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

