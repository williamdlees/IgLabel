# Script to manage IG allele labels, using a csv file 'database'


import argparse
from datetime import datetime

import simple_bio_seq as simple
import csv
import os.path
import re

parser = argparse.ArgumentParser(description='Manage allocation of temporary allele labels within a species or strain')
subparsers = parser.add_subparsers(help='Desired action to perform', dest='action')
parent_parser = argparse.ArgumentParser(add_help=False)

parser_create = subparsers.add_parser('create', parents=[parent_parser], help='Create database')
parser_create.add_argument('database_file', help='allocation database')

parser_query = subparsers.add_parser('query', parents=[parent_parser], help='Query database')
parser_query.add_argument('database_file', help='allocation database')
parser_query.add_argument('query_file', help='list of sequences to query (FASTA)')
parser_query.add_argument('result_file', help='list of results (CSV)')
parser_query.add_argument('action_file', help='list of results (CSV)')

parser_add = subparsers.add_parser('add', parents=[parent_parser], help='Add sequences to database')
parser_add.add_argument('database_file', help='allocation database')
parser_add.add_argument('action_file', help='list of sequences to add (FASTA)')
parser_add.add_argument('contributor', help='Name of contributor')
parser_add.add_argument('result_file', help='list of results (CSV)')


# database columns

label_database_cols = [
    'label',            # the allocated label
    'sequences',        # sequences allocated to this label, separated by a comma
    'longest_seq',      # the longest sequence allocated to this label
    'contributor',      # name of original sequence contributor
    'first_added',      # date first added
    'last_updated',     # date last updated
]


def create_database(args):
    print('Creating database "%s"' % args.database_file)

    if os.path.exists(args.database_file):
        print('Error: database exists already.')
        return

    with open(args.database_file, 'w', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=label_database_cols)
        writer.writeheader()
        print('Database created.')

    return


def read_label_database(database_file):
    if not os.path.isfile(database_file):
        print('Error: database "%s" not found' % database_file)
        return None

    label_database = {}

    with open(database_file, 'r') as fi:
        reader = csv.DictReader(fi)
        for row in reader:
            label_database[row['label']] = row

    return label_database


def write_label_database(label_database, database_file):
    if '.' in database_file:
        backup_database_file = database_file.replace('.', '_old.')
    else:
        backup_database_file = database_file + '_old'

    if os.path.isfile(backup_database_file):
        os.remove(backup_database_file)

    os.rename(database_file, backup_database_file)

    with open(database_file, 'w', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=label_database_cols)
        writer.writeheader()
        for row in label_database.values():
            writer.writerow(row)

    print('Database written to %s. Previous version saved as %s' % (database_file, backup_database_file))


# replace the list of sequences provided in the database against a label with just one,
# which will be the longest sequence listed.

def read_seqs(sequence_file):
    if not os.path.isfile(sequence_file):
        print('Error: sequence file "%s" not found' % sequence_file)
        return None

    seqs = simple.read_fasta(sequence_file)

    return seqs


query_result_cols = [
    'seq_id',               # query sequence id
    'sequence',             # query sequence
    'match',                # match type (blank, exact, query_is_existing_sub, query_is_new_sub, query_is_super, invalid_nuc)
    'matched_label',        # matched sequence label
    'matched_sequence'      # matched sequence
]

action_table_cols = [
    'seq_id',               # query sequence id
    'sequence',             # query sequence
    'action',               # action to take ('none', 'new_label', 'add_new_subset', 'add_new_superset')
    'label',                # label to modify (or blank for new)
    'reason',               # result code (from query_result_cols) that leads to this action
]

# define what action to recommend if there is >1 match in the database. Lowest score has priority.

actions_and_priorities = {
    'invalid_nuc': ('none', 1),       # highest priority - never take any action on a sequence with invalid nucleotides
    'exact': ('none', 2),
    'query_is_existing_sub': ('none', 3),
    'query_is_super': ('add_new_superset', 4),
    'query_is_new_sub': ('add_new_subset', 5),
    'no_match': ('new_label', 6)
}


def query_database(args):
    print('Querying database "%s" for sequences in "%s"' % (args.database_file, args.query_file))

    label_database = read_label_database(args.database_file)
    query_seqs = read_seqs(args.query_file)

    if label_database is None or query_seqs is None:
        return

    with open(args.result_file, 'w', newline='') as fo, open(args.action_file, 'w', newline='') as fa:
        res_writer = csv.DictWriter(fo, fieldnames=query_result_cols)
        res_writer.writeheader()
        act_writer = csv.DictWriter(fo, fieldnames=action_table_cols)
        act_writer.writeheader()

        for seq_id, seq in query_seqs.items():
            res = {'seq_id': seq_id, 'sequence': seq, 'match': '', 'matched_label': '', 'matched_sequence': ''}
            action = {'seq_id': seq_id, 'sequence': seq, 'action': 'new_label', 'label': '', 'reason': 'no_match'}
            m = re.search('[^ACGT]', seq)
            if m is not None:
                res['match'] = 'invalid_nuc'
                res_writer.writerow(res)
                action['action'] = actions_and_priorities[res['match']]
                action['reason'] = res['match']
                act_writer.writerow(action)
            else:
                for row in label_database.values():
                    res['match'] = ''
                    if seq == row['longest_seq']:
                        res['match'] = 'exact'
                    elif seq in row['longest_seq']:
                        res['match'] = 'query_is_new_sub'
                        for sub_seq in row['sequences'].split(','):
                            if seq == sub_seq:
                                res['match'] = 'query_is_existing_sub'
                                break
                    elif row['longest_seq'] in seq:
                        res['match'] = 'query_is_super'

                    if res['match'] != '':
                        res['matched_label'] = row['label']
                        res['matched_sequence'] = row['longest_seq']
                        res_writer.writerow(res)
                        if actions_and_priorities[res['match']][1] < actions_and_priorities[action['reason'][1]]:
                            action['action'] = actions_and_priorities[res['match']]
                            action['label'] = res['matched_label']
                            action['reason'] = res['match']

                act_writer.writerow(action)


def generate_new_label(label_database):
    return('foo')

def add_database(args):
    label_database = read_label_database(args.database_file)

    if label_database is None:
        return

    if not os.path.isfile(args.action_file):
        print('Action file "%s" not found' % args.action_file)
        return

    # before we go any further, conduct some sanity checks on the action file


    with open(args.action_file, 'r') as fi:
        reader = csv.DictReader(fi)
        for row in reader:
            if row['label'] != '' and row['label'] not in label_database:
                print('Error: the action file refers to label %s, which is not in the database. The action file has not been processed.')
                return
            if len(row['sequence']) == 0 or re.search('[^ACGT]', row['sequence']) is not None:
                print('Error: sequence id %s has an invalid sequence (sequences may only contain the letters ACGT and may not be blank. The action file has not been processed.' % row['seq_id'])
                return
            if row['action'] not in ['none', 'add_new_superset', 'add_new_subset', 'new_label']:
                print('Error: the action file contains an invalid action "%s". The action file has not been processed.' % row['action'])
                return

    with open(args.action_file, 'r') as fi:
        reader = csv.DictReader(fi)
        timestamp = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
        for row in reader:
            if row['action'] == 'new_label':
                entry = {
                    'label': generate_new_label(label_database),
                    'sequences': row['sequence'],
                    'longest_seq': row['sequence'],
                    'contributor': args.contributor,
                    'first_added': timestamp,
                    'last_updated': timestamp,
                }
                label_database[entry['label']] = entry
            elif row['action'] == 'add_new_subset':
                if row['sequence'] not in label_database[row['label']]['longest']:
                    print('Error. Sequence id %s is not a subset of label %s. Action ignored.' % (row['seq_id'], row['label']))
                    continue
                for seq in label_database[row['label']]['sequences']:
                    if seq == row['sequence']:
                        print('Warning. Sequence id %s is already a listed subset of label %s. Action ignored.' % (row['seq_id'], row['label']))
                        continue

                label_database[row['label']]['sequences'] += ',' + row['sequence']
            elif row['action'] == 'add_new_superset':
                if label_database[row['label']]['longest'] not in row['sequence']:
                    print('Error. Sequence id %s is not a superset of label %s. Action ignored.')
                    continue

                label_database[row['label']]['sequences'] += ',' + row['sequence']
                label_database[row['label']]['longest'] = row['sequence']

    write_label_database(label_database, args.database_file)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.action == 'create':
        create_database(args)
    elif args.action == 'query':
        query_database(args)
    elif args.action == 'add':
        add_database(args)

