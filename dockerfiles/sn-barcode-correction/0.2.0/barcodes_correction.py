"""
snATAC-seq barcodes orientation detection and correction
by comparing with whitelist and allowing up to 1 Hamming
distance between observed and expected sequences
"""

## -- Imports --
import os
import gzip
from collections import Counter
from itertools import product
from multiprocessing import Pool
from Bio.SeqIO.QualityIO import FastqGeneralIterator
import argparse
from collections import defaultdict

## -- Arguments parser --
def parse_args():
    parser = argparse.ArgumentParser(description="Barcode correction for 10X snATAC-seq")
    parser.add_argument("-f", "--fastq", required=True, help="Path to uncompressed FASTQ file containing the barcodes (e.g., R2)")
    parser.add_argument("-w", "--whitelist", required=True, help="Path to the 10X whitelist file")
    parser.add_argument("-o", "--out_corrected", required=True, help="Path to the output FASTQ file with corrected barcodes")
    parser.add_argument("-u", "--out_uncorrected", required=True, help="Path to the output text file with the uncorrected barcodes")
    parser.add_argument("-t", "--offset", type=int, default=0, help="Number of bases after which the barcode start in the read")
    parser.add_argument("-p", "--processes", type=int, default=4, help="Number of processes for multiprocessing (default = 4)")
    parser.add_argument("-s", "--chunk_size", type=int, default=500000, help="Number of reads per chunk for parallel processing (default = 500000)")
    parser.add_argument("-n", "--sample_size", type=int, default=500000, help="Size of the random sample of barcodes for determining their orientation (default = 500000)")
    parser.add_argument("-q", "--min_quality", type=float, default=0.9, help="Minimum correction confidence (default = 0.9)")
    parser.add_argument("-d", "--min_prop_dir", type=float, default=0.6, help="Minimum proportion for deciding barcode orientation (default = 0.6)")
    return parser.parse_args()

#############
## Helpers ##
#############

BASE2BIT = {'A':0, 'C':1, 'G':2, 'T':3}
BIT2BASE = "ACGT"

## -- Handle compressed files --
def open_file(path, mode='rt'):
    return gzip.open(path, mode) if path.endswith('.gz') else open(path, mode)

## -- Reverse and complement --
def reverse_complement(seq):
    """Reverse and complement a DNA sequence"""
    comp = str.maketrans("ACGT", "TGCA")
    return seq.translate(comp)[::-1]

## -- Encode and decode barcodes --
def encode_barcode(seq):
    x = 0
    for b in seq:
        x = (x << 2) | BASE2BIT[b]
    return x

def decode_barcode(x, length):
    out = []
    for _ in range(length):
        out.append(BIT2BASE[x & 3])
        x >>= 2
    return ''.join(reversed(out))

## -- Detected Phred offset --
def detect_phred_offset(fastq_file, n_reads=1000):
    """
    Detect whether FASTQ quality scores are Phred+33 or Phred+64.
    Reads up to n_reads records and checks ASCII range.
    """
    min_q, max_q = 126, 0  # ASCII range
    with open_file(fastq_file, "rt") as handle:
        for i, (_, _, qual) in enumerate(FastqGeneralIterator(handle)):
            for ch in qual:
                asc = ord(ch)
                min_q = min(min_q, asc)
                max_q = max(max_q, asc)
            if i >= n_reads:
                break

    if min_q < 59:   # below ';' is almost always Phred+33
        return 33
    else:
        return 64 

## -- Decoding Phred score --
def phred_prob(qchar):
    """Return probability of sequencing error for a base call"""
    q = min(ord(qchar) - PHRED_OFFSET, 66)  # Illumina Phred+33, cap at 66
    p_error = 10 ** (-q / 10.0)
    return p_error

## -- Defining Hamming neighbors --
def hamming1_neighbors(enc, length):
    for i in range(length):
        shift = 2 * (length - i - 1)
        orig = (enc >> shift) & 3
        for alt in (0,1,2,3):
            if alt != orig:
                yield enc ^ ((orig ^ alt) << shift), i

## -- retrieve lookup for observed barcodes --
def lookup_candidates_for_observed(bc_seq):
    """
    Return exact-match candidates for an observed sequence.
    If obs_seq contains a single 'N', expand N -> A/C/G/T and return only candidates
    from the whitelist that match exactly (mismatch_idx is None).
    """
    # handle N explicitly
    if 'N' in bc_seq:
        if bc_seq.count('N') > 1:
            return []
        i = bc_seq.index('N')
        out = []
        for b in "ACGT":
            s = bc_seq[:i] + b + bc_seq[i+1:]
            enc = encode_barcode(s)
            if enc in WHITELIST_ENC:
                out.append((enc, None))
        return out

    enc = encode_barcode(bc_seq)

    if enc in WHITELIST_ENC:
        return [(enc, None)]

    hits = []
    for neigh, idx in hamming1_neighbors(enc, BC_LEN):
        if neigh in WHITELIST_ENC:
            hits.append((neigh, idx))
    return hits

## -- Barcode direction detection --
def barcodes_match(fastq_file, whitelist,sample_size,offset, thresh):
    """Identify the barcodes orientation and report if reverse and complement is needed"""
    rc_whitelist = {reverse_complement(bc) for bc in whitelist}
    bc_match = 0
    bcrc_match = 0
    chunk = next(load_chunks(fastq_file, sample_size))
    sample_size = min(sample_size, len(chunk))
    for title, bc, qual in chunk:
        if bc[offset:] in whitelist:
            bc_match += 1
        if bc[offset:] in rc_whitelist:
            bcrc_match += 1
    bc_match_prop = bc_match / sample_size
    bcrc_match_prop = bcrc_match / sample_size
    valid = (bc_match_prop >= thresh) or (bcrc_match_prop >= thresh)
    rc_need = (bcrc_match_prop >= bc_match_prop)
    print(f"Direct match proportion: {bc_match_prop}\n")
    print(f"Reverse-complement match proportion: {bcrc_match_prop}\n")
    print(f"Reverse-complement required: {rc_need}\n")
    return(rc_need)

# --- Global barcode counts ---
def build_barcode_counts(fastq_file, offset, rc_need):
    """Assign total counts to each observed barcode"""
    counts = Counter()
    with open_file(fastq_file, "rt") as handle:
        for _, seq, qual in FastqGeneralIterator(handle):
            bc_seq = seq[offset:]
            if rc_need:
                bc_seq = reverse_complement(bc_seq)
            counts[bc_seq] += 1
    return counts

###############################################
## Helpers for parallel and chunk processing ##
###############################################    

## -- Variables initializer --
def init_worker(whitelist_enc, enc_to_bc, bc_counts_enc, prob_threshold, offset, rc_need, phred_offset, bc_len):
    """Initialise the global variables in each parallel process"""
    global WHITELIST_ENC, ENC2BC, BARCODE_COUNTS, TOTAL_COUNT
    global PROB_THRESHOLD, OFFSET, RC_NEED, PHRED_OFFSET, BC_LEN
    WHITELIST_ENC = whitelist_enc
    ENC2BC = enc_to_bc
    BARCODE_COUNTS = bc_counts_enc
    PROB_THRESHOLD = prob_threshold
    OFFSET = offset
    RC_NEED = rc_need
    PHRED_OFFSET = phred_offset
    BC_LEN = bc_len 
    alpha = 1.0 # for smoothing prior calculation
    TOTAL_COUNT = sum(BARCODE_COUNTS.values()) + alpha * len(WHITELIST_ENC)  # for prior calculation

## -- Load reads chunk --
def load_chunks(file_path, chunk_size):
    """Load a chunk of reads for parallel processing"""
    with open_file(file_path, "rt") as handle:
        chunk = []
        for record in FastqGeneralIterator(handle):
            chunk.append(record)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

######################
## Chunk processing ##
######################

## -- Barcode correction --
def process_chunk(chunk):
    """If needed, barcodes are reversed and complemented and then corrected to match whitelist"""
#    print(f"[PID {os.getpid()}] Starting chunk with {len(chunk)} reads.")
    corrected = []
    uncorrected = []
    alpha = 1.0 # for smoothing prior calculation
    #total_count = sum(BARCODE_COUNTS.values()) + alpha * len(WHITELIST_ENC)  # for prior calculation
    n_exact_match = 0
    n_corrected = 0
    n_uncorrected = 0
    for title, seq, qual in chunk:
        bc_seq = seq[OFFSET:]  # selecting barcode sequencing
        bc_qual = qual[OFFSET:]  # selecting barcode read quality
        if RC_NEED: 
            bc_seq = reverse_complement(bc_seq)
            bc_qual = bc_qual[::-1]
        candidates = lookup_candidates_for_observed(bc_seq)
        # Variables that will be returned at the end. Default: uncorrected seq and qual
        final_bc = bc_seq
        final_qual = bc_qual
        mark_uncorrected = False
        # case 1: no matches with whitelist (including 1-Hamming dist)
        if not candidates:
            mark_uncorrected = True
        # case 2: Single match with whitelist (including 1-Hamming dist)
        elif len(candidates) == 1:
            enc, idx = candidates[0]
            final_bc = ENC2BC[enc]
            # Exact match
            if idx is None:
                n_exact_match += 1
            # Mismatch
            else:
                n_corrected += 1                
        else:
            # case 3: Multiple matches with whitelist (including 1-Hamming dist), one is perfect
            perfect_matches = [enc for enc, idx in candidates if idx is None]
            if perfect_matches:
                final_bc = ENC2BC[perfect_matches[0]] # one of the candidates is a perfect match
                n_exact_match += 1
            else:
             # case 4: Multiple matches with whitelist (all 1-Hamming dist)   
            # Compute posterior probabilities
                posteriors = []
                priors = []
                for enc, mismatch_idx in candidates:
                    prior = (BARCODE_COUNTS.get(enc, 0) + alpha) / TOTAL_COUNT # total_count # Laplace smoothing
                    q_prob = phred_prob(bc_qual[mismatch_idx]) 
                    wbc = ENC2BC[enc]
                    posteriors.append((wbc, prior * q_prob))
                    priors.append((wbc, BARCODE_COUNTS.get(wbc, 0))) # only for debug
                total_score = sum(score for _, score in posteriors)
                if total_score > 0:
                    # normalise posterior probabilities
                    posteriors = [(wbc, score / total_score) for wbc, score in posteriors]
                    best_barcode, best_prob = max(posteriors, key=lambda x: x[1])
                    if best_prob >= PROB_THRESHOLD:# and expected_errors < MAX_EXPECTED_ERRORS:
                        final_bc = best_barcode # choose the best
                        n_corrected += 1
                    else:
                        mark_uncorrected = True # do not choose a matching barcode in the whitelist
                else:
                    mark_uncorrected = True # do not choose a matching barcode in the whitelist
        if mark_uncorrected: # report here the ones without correction and not in the whitelist
            n_uncorrected += 1
            uncorrected.append((title, final_bc, final_qual))
        corrected.append((title, final_bc, final_qual))
    return corrected, uncorrected, n_exact_match, n_corrected, n_uncorrected

## ----------- main --------- ##

if __name__ == "__main__":
    args = parse_args()
    fastq_file = args.fastq
    whitelist_file = args.whitelist
    corrected_file = args.out_corrected
    uncorrected_file =args.out_uncorrected
    offset = args.offset
    num_cores = args.processes
    prob_threshold = args.min_quality
    chunk_size = args.chunk_size
    sample_size = args.sample_size
    min_prop_dir = args.min_prop_dir

    # loading whitelist
    with open_file(whitelist_file) as f:
        whitelist = [line.strip() for line in f if line.strip()]
    # compute barcodes length
    bc_len = len(whitelist[0])        
    # determine if reverse and complement operation is needed
    rc_need = barcodes_match(fastq_file, set(whitelist), sample_size, offset, min_prop_dir)
    print("Barcodes reverse and complement status:", rc_need)
    
    # detect Phred scores offset
    phred_offset = detect_phred_offset(fastq_file, sample_size)
    
    # generate barcode counts
    barcode_counts = build_barcode_counts(fastq_file, offset, rc_need)

    # sequence encoding
    whitelist_enc = set()
    enc2bc = {}
    for bc in whitelist:
        e = encode_barcode(bc)
        whitelist_enc.add(e)
        enc2bc[e] = bc

    bc_counts_enc = Counter()
    for bc, c in barcode_counts.items():
        if 'N' not in bc:
            bc_counts_enc[encode_barcode(bc)] = c

    
    # create a pool of parallel processes
    pool = Pool(processes = num_cores,
                initializer = init_worker,
                initargs = (whitelist_enc, enc2bc, bc_counts_enc,
                        prob_threshold, offset, rc_need,
                        phred_offset, bc_len))
    
    print(f"Running barcode correction with {num_cores} processes...")
    
    # barcodes processing
    n_match = 0
    n_corrected = 0
    n_uncorrected = 0
    with open_file(corrected_file, "wt") as out_corr, open_file(uncorrected_file, "wt") as out_uncorr:
        for corrected_chunk, uncorrected_chunk, n_match_chunk, n_corr_chunk, n_uncorr_chunk in pool.imap(process_chunk, load_chunks(fastq_file, chunk_size)):
            # write corrected barcodes
            for title, seq, qual in corrected_chunk:
                out_corr.write(f"@{title}\n{seq}\n+\n{qual}\n")
            # write uncorrected barcodes
            for title, seq, _ in uncorrected_chunk:
                out_uncorr.write(f"@{title}\n{seq}\n")
            n_match += n_match_chunk
            n_corrected += n_corr_chunk
            n_uncorrected += n_uncorr_chunk
    
    pool.close()
    pool.join()
    print("Finished writing corrected FASTQ:", corrected_file)
    print("Finished writing uncorrected FASTQ:", uncorrected_file)
    print("Number of barcodes with exact match:", n_match)
    print("Number of corrected barcodes:", n_corrected)
    print("Number of barcodes without match:", n_uncorrected)

