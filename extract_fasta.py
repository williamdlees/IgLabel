import argparse
import simple_bio_seq as simple

parser = argparse.ArgumentParser(description='Extract the longest sequence for each allocated label in FASTA format')
parser.add_argument('database_file', help='allocation database')
parser.add_argument('output_file', help='output file (FASTA)')
parser.add_argument('prefix', help='prefix for names (e.g. IGHV_')

args = parser.parse_args()

db = simple.read_csv(args.database_file)
seqs = {}

for db_rec in db:
    seqs[args.prefix + db_rec['label']] = db_rec['longest_seq']

simple.write_fasta(seqs, args.output_file)
