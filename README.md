# IgLabel
##Manage allocation of temporary labels for IG alleles

This script will allocate 'temporary labels' for newly discovered IG alleles in accordance with 
the schema and process defined by the 
[Germline Database Working Group](https://www.antibodysociety.org/the-airr-community/airr-working-groups/germline_database/) 
of the 
[AIRR Community](https://www.antibodysociety.org/the-airr-community/). This is an experimental 
work-in-progress.

Draft documents omn which it is based:

Outline schema for germline database management: 
- [document](), [schema]() (links not working as yet, to be updated)
- [Specification for this script](https://docs.google.com/document/d/1Top32CXCL2uOyjfHl54ebJEG43Jnc2oAoRjq5e6niEA/edit?usp=sharing)

##Installation

The script requires Python 3.6 or later, with BioPython installed. Clone the repo to your workstation to use it.

## Usage

The script supports three commands: `create`, `query`, `add`

```
usage: iglabel.py [-h] {create,query,add} ...

Manage allocation of temporary allele labels within a species or strain

positional arguments:
  {create,query,add}  Desired action to perform
    create            Create database
    query             Query database
    add               Add sequences to database

optional arguments:
  -h, --help          show this help message and exit
```

## Example Usage
For a brief tour of its capabilities, open a command prompt and cd to the directory IgLabel/test.

The script is intended to maintain a database for a specific strain or species. You can give 
the database any name you want, as long as it is a valid filename. As the database is a CSV file,
it's convenient to give it a name ending in .csv.  You create a new database with the 
`create` command:

```
IgLabel\test>python ..\iglabel.py create mouse_b6.csv
Creating database "mouse_b6.csv"
Database created.
```

The `query` command takes a set of sequences, in a FASTA file, and checks them against the database.
It produces a summary file, listing sequence matches and non-matches, and an actions file, which 
lists the suggested actions, where necessary, to add the sequences to the database and generate
new labels as required. The file seq1.fasta contains two (very short and simple) sequences. As the 
database is empty at the moment, if we run a query with this file it will tell us that neither
sequence is found in the database and that both should be added.

```
usage: iglabel.py query [-h] database_file query_file result_file action_file

positional arguments:
  database_file  allocation database
  query_file     list of sequences to query (FASTA)
  result_file    list of results (CSV)
  action_file    list of results (CSV)

optional arguments:
  -h, --help     show this help message and exit
```
```
IgLabel\test>python ..\iglabel.py query mouse_b6.csv seq1.fasta results.csv actions.csv
Querying database "mouse_b6.csv" for sequences in "seq1.fasta"
```
Here are the contents of the results file:

And the actions file:



