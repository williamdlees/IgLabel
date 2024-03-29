# Wrapper around BioSeq functions for simple applications
# principles:
# - store sequences as strings, use dicts for collectiopns
# - all sequences are coerced to upper case on input
# - iterators are coreced into lists for ease of debugging
# basically just make things simple for cases where we don't need to do more

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment, AlignInfo
import random
import csv


def read_fasta(infile):
    res = {}
    recs = SeqIO.parse(infile, 'fasta')
    for rec in recs:
        res[rec.id] = str(rec.seq).upper()
    return res


def write_fasta(seqs, outfile):
    SeqIO.write(toSeqRecords(seqs), outfile, 'fasta')


def read_single_fasta(infile):
    res = ''
    recs = SeqIO.parse(infile, 'fasta')
    for rec in recs:
        return str(rec.seq).upper()


# read V,D,J regions from one or more species from an IMGT reference file
# species should be a ***list*** of species
# returns a nested dict: [species][chain]
def read_imgt_fasta(infile, species, chains=['IGHV', 'IGHD', 'IGHJ']):
    res = {}
    for sp in species:
        res[sp] = {}
        for chain in chains:
            res[sp][chain] = {}

    recs = SeqIO.parse(infile, 'fasta')

    for rec in recs:
        for sp in species:
            for chain in chains:
                if '-REGION' in rec.description and sp in rec.description and chain in rec.description:
                    if 'V' not in chain or len(rec.seq) > 280:       # strip out obviously incomplete Vs
                        name = rec.description.split('|')[1]
                        res[sp][chain][name] = str(rec.seq).upper()
    return res


def sample_fasta(seqs, number):
    keys = seqs.keys()

    if len(keys) <= number:
        return seqs

    sample = random.sample(keys, number)
    sample_seqs = {}
    for key in sample:
        sample_seqs[key] = seqs[key]
    return sample_seqs


def translate(seq, truncate=True):
    seq_len = len(seq)
    residue = seq_len % 3

    if residue != 0:
        if truncate:
            seq = seq[:seq_len - residue]
        else:
            seq += 'N' * (3 - residue)

    return Seq(seq).translate()


def reverse_complement(seq):
    return str(Seq(seq).reverse_complement())


def nt_diff(s1, s2):
    diffs = 0
    row = list(zip(s1.upper(), s2.upper()))

    for p in range(len(row)):
        if row[p][0] != row[p][1] and (row[p][0] not in ['X', 'N'] and row[p][1] not in ['X', 'N']):
            diffs += 1

    diffs += abs(len(s1) - len(s2))
    return diffs


# convert our dict format to SeqRecords
def toSeqRecords(seqs):
    recs = []
    for name, seq in seqs.items():
        recs.append(SeqRecord(Seq(seq), id=name, description=''))
    return recs


def dumb_consensus(seqs, threshold):
    msa = MultipleSeqAlignment(toSeqRecords(seqs))
    summary_align = AlignInfo.SummaryInfo(msa)
    return summary_align.dumb_consensus(threshold=threshold)


# Read csv file into a list of dicts
def read_csv(file, delimiter=None):
    ret = []
    with open(file, 'r') as fi:
        if delimiter:
            reader = csv.DictReader(fi, delimiter=delimiter)
        else:
            reader = csv.DictReader(fi)
        for row in reader:
            ret.append(row)

    return ret


# Write csv file given a list of dicts. Fieldnames are taken from the first row
def write_csv(file, rows, delimiter=None):
    if not rows:
        return

    fieldnames = rows[0].keys()
    with open(file, 'w', newline='') as fo:
        if delimiter:
            writer = csv.DictWriter(fo, fieldnames=fieldnames, delimiter=delimiter)
        else:
            writer = csv.DictWriter(fo, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            writer.writerow(row)
