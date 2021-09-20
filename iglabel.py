# Script to manage IG allele labels, using a csv file 'database'


import argparse
import simple_bio_seq as simple
import csv
import sys

parser = argparse.ArgumentParser(description='Manage allocation of temporary allele labels within a species or strain')

subparsers = parser.add_subparsers(help='Desired action to perform', dest='action')

parent_parser = argparse.ArgumentParser(add_help=False)

parser_create = subparsers.add_parser('create', parents=[parent_parser], help='Create database')
parser_create.add_argument('database_file', help='allocation database')

parser_query = subparsers.add_parser('query', parents=[parent_parser], help='Query database')
parser_query.add_argument('database_file', help='allocation database')
parser_query.add_argument('query_file', help='list of sequences to query (FASTA)')
parser_query.add_argument('result_file', help='list of results (CSV)')

parser_add = subparsers.add_parser('add', parents=[parent_parser], help='Add sequences to database')
parser_add.add_argument('database_file', help='allocation database')
parser_add.add_argument('sequence_file', help='list of sequences to add (FASTA)')
parser_add.add_argument('contributor', help='Name of contributor')
parser_add.add_argument('result_file', help='list of results (CSV)')
parser_add.add_argument('--dry_run', help='perform a trial run with no changes made', action='store_false', required=False)
parser_add.add_argument('--force', help='allocate new labels for each sequence even if a potential alias exists', action='store_false', required=False)




# database columns

label_database_cols = [
    'label',            # the allocated label
    'sequences',        # sequences allocated to this label
    'contributor',      # name of original sequence contributor
    'first_added',      # date first added
    'last_updated',     # date last updated
]


def create_database(args):
    return


def query_database(args):
    return


def add_database(args):
    return


if __name__ == "__main__":
    args = parser.parse_args()

    if args['action'] == 'create':
        create_database(args)
    elif args['action'] == 'query':
        query_database(args)
    elif args['action'] == 'add':
        add_database(args)

