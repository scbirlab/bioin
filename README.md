# 💻 bioino

![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/scbirlab/bioino/python-publish.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bioino)
![PyPI](https://img.shields.io/pypi/v/bioino)

Command-line tools and Python API for interconverting FASTA, GFF, and CSV. 

**bioino** currently converts tables to FASTA, and GFF to tables. Also provides 
a Python API for handling GFF and FASTA files, and converting to table
files.

_Warning_: **bioino** is under active development, and not fully tested, so 
things may change, break, or simply not work.

## Installation

### The easy way

Install the pre-compiled version from PyPI:

```bash
pip install bioino
```

### From source

Clone the repository, then `cd` into it. Then run:

```bash
pip install -e .
```

## Usage

### Command line

Convert CSV or XLSX of sequences to a FASTA file. Info goes to `stderr`, so you can pipe the output you
want to other tools or to a file.

```bash
$ printf 'name\tseq\tdata\nSeq1\tAAAAA\tSome-info\n' | bioino table2fasta -n name -s seq -d data
🚀 Generating FASTA from tables with the following parameters:
        subcommand: table2fasta
        input: <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>
        format: TSV
        sequence: seq
        name: ['name']
        description: ['data']
        worksheet: Sheet 1
        output: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
        func: <function _table2fasta at 0x7f4b48a43d30>
>Seq1 data=Some-info
AAAAA
⏰ Completed process in 0:00:00.025771
```

Convert GFF tables to TSV (or CSV).

```bash
$ printf 'test_seq\ttest_source\tgene\t1\t10\t.\t+\t.\tID=test01;attr1=+\n' | bioino gff2table 2> /dev/null
seqid   source  feature start   end     score   strand  phase   ID      attr1
test_seq        test_source     gene    1       10      .       +       .       test01  +

$ printf 'test_seq\ttest_source\tgene\t1\t10\t.\t+\t.\tID=test01;attr1=+\n' | bioino gff2table -f CSV 2> /dev/nul
l
seqid,source,feature,start,end,score,strand,phase,ID,attr1
test_seq,test_source,gene,1,10,.,+,.,test01,+
```

#### Detailed usage

```bash
$ bioino --help
usage: bioino [-h] {gff2table,table2fasta} ...

Interconvert some bioinformatics file formats.

optional arguments:
  -h, --help            show this help message and exit

Sub-commands:
  {gff2table,table2fasta}
                        Use these commands to specify the tool you want to use.
    gff2table           Convert a GFF to a TSV file.
    table2fasta         Convert a CSV or TSV of sequences to a FASTA file.
```

```bash
$ bioino gff2table --help
usage: bioino gff2table [-h] [--format {TSV,CSV}] [--metadata] [--output OUTPUT] [input]

positional arguments:
  input                 Input file in GFF format. Default: "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>".

optional arguments:
  -h, --help            show this help message and exit
  --format {TSV,CSV}, -f {TSV,CSV}
                        File format. Default: "TSV".
  --metadata, -m        Write GFF header as commented lines.
  --output OUTPUT, -o OUTPUT
                        Output file. Default: STDOUT
```

```bash
$ bioino table2fasta --help
usage: bioino table2fasta [-h] [--format {TSV,CSV}] [--sequence SEQUENCE] --name [NAME [NAME ...]]
                          [--description [DESCRIPTION [DESCRIPTION ...]]] [--worksheet WORKSHEET] [--output OUTPUT]
                          [input]

positional arguments:
  input                 Input file in GFF format. Default: "<_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>".

optional arguments:
  -h, --help            show this help message and exit
  --format {TSV,CSV}, -f {TSV,CSV}
                        File format. Default: "TSV".
  --sequence SEQUENCE, -s SEQUENCE
                        Column to take sequence from. Default: "sequence".
  --name [NAME [NAME ...]], -n [NAME [NAME ...]]
                        Column(s) to take sequence name from. Concatenates values with "_", replaces spaces with "-". Required.
  --description [DESCRIPTION [DESCRIPTION ...]], -d [DESCRIPTION [DESCRIPTION ...]]
                        Column(s) to take sequence description from. Concatenates values with ";", replaces spaces with "_".
                        Default: don't use.
  --worksheet WORKSHEET, -w WORKSHEET
                        For XLSX files, the worksheet to take the table from. Default: "Sheet 1".
  --output OUTPUT, -o OUTPUT
                        Output file. Default: STDOUT
```

### Python API

#### FASTA

Read FASTA files (or strings) into iterators of named tuples.

```python
>>> from bioino import FastaSequence, FastaCollection

>>> seq1 = FastaSequence("example", "This is a description", "ATCG")
>>> seq1
FastaSequence(name='example', description='This is a description', sequence='ATCG')
>>> seq2 = FastaSequence("example2", "This is another sequence", "GGGAAAA")
>>> fasta_stream = FastaCollection([seq1, seq2])
>>> fasta_stream
FastaCollection(sequences=[FastaSequence(name='example', description='This is a description', sequence='ATCG'), FastaSequence(name='example2', description='This is another sequence', sequence='GGGAAAA')])

```

These objects show as FASTA format when written, toptionally to a file.

```python
>>> fasta_stream.write()  
>example This is a description
ATCG
>example2 This is another sequence
GGGAAAA
```

#### GFF

Makes an attempt to conform to GFF3 but makes no guarantees.

Similar to the FSAT utiities, GFF is read into an object.

```python
>>> from io import StringIO
>>> from bioino import GffFile

>>> lines = ["##meta1 item1", 
...          "#meta2  item2  comment", 
...          '\t'.join("test_seq    test_source gene    1   10  .   +   .   ID=test01;attr1=+".split()),
...          '\t'.join("test_seq    test_source gene    9   100  .   +   .   Parent=test01;attr2=+".split())]
>>> file = StringIO()
>>> for line in lines:
...     print(line, file=file)
>>> gff = GffFile.from_file(file)
```

These render as GFF lines when printed.

```python
>>> gff.write()  
##meta1 item1
#meta2  item2  comment
test_seq   test_source     gene    1       10      .       +       .       ID=test01;attr1=+
test_seq   test_source     gene    9       100     .       +       .       Parent=test01;attr2=+

```

#### GFF lookup table

An iterable of `GffLine`s can be converted into a lookup table mapping
chromosome location to feature annotations. Regions without annotation
are automatically filled with references to upstream or 
downstream features.

Just create a `GffFile` with `lookup=True`, or use the `_lookup_table()` method of an instantiated `GffFile`.

There are currently some limitations:
- Currently only works for single-chromosome files.
- Only references parent features. Child features not yet indexed.
- Will not work for GFFs with a single parent feature.
- Ignores the following feature types: "region", :repeat_region"

#### Interconversion

`GFFLine`s can be converted to dictionaries and vice versa.

```python
>>> from bioino import GffLine

>>> d = dict(seqid='TEST', source='test', feature='gene', start=1, end=100, score='.', strand='+', phase='+')
>>> print(GffLine.from_dict(d))
TEST        test    gene    1       100     .       +       +
>>> d.update(dict(ID='test001', comment='This is a test'))
>>> GffLine.from_dict(d).write() 
TEST    test    gene    1       100     .       +       +       ID=test001;comment=This is a test
```

```python
>>> from io import StringIO
>>> from bioino import GffFile

>>> file = StringIO()
>>> lines = ["TEST    test    gene    1       100     .       +       +  ID=test001;comment=Test".split(),
...          "TEST2    test2    gene    101       200     .       +       +  ID=test002;comment=Test2".split()]
>>> for line in lines:
...     print('\t'.join(line), file=file)
>>> list(GffFile.from_file(file).as_dict())  
[{'seqid': 'TEST', 'source': 'test', 'feature': 'gene', 'start': 1, 'end': 100, 'score': '.', 'strand': '+', 'phase': '+', 'ID': 'test001', 'comment': 'Test'}, {'seqid': 'TEST2', 'source': 'test2', 'feature': 'gene', 'start': 101, 'end': 200, 'score': '.', 'strand': '+', 'phase': '+', 'ID': 'test002', 'comment': 'Test2'}]
         

```

And Pandas DataFrames can be converted to FASTA.

```python
>>> import pandas as pd

>>> df = pd.DataFrame(dict(seq=['atcg', 'aaaa'], 
...                  title=['seq1', 'seq2'], 
...                  info=['SeqA', 'SeqB'], 
...                  score=[1, 2]))
>>> df 
        seq title  info  score
0  atcg  seq1  SeqA      1
1  aaaa  seq2  SeqB      2
>>> FastaCollection.from_pandas(df, sequence='seq', 
...                             names=['title'], 
...                             descriptions=['info', 'score']).write() 
>seq1 info=SeqA;score=1
atcg
>seq2 info=SeqB;score=2
aaaa
```

## Suggestions, issues, fixes

File an issue [here](https://github.com/scbirlab/bioino).

## Documentation

Check the API [here](https://bioino.readthedocs.org).