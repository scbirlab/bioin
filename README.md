# 💻 bioino

Interconverting FASTA, GFF, and CSV. 

Currently converts tables to FASTA, and GFF to tables. Also provides 
a Python API for handling GFF and FASTA files, and converting to table
files.

_Warning_: Bioin is under active development, and not fully tested, so 
things may change, break, or simply not work.

## Installation

### The easy way

Install the pre-compiled version from PyPI:

```bash
pip install bioin
```

### From source

Clone the repository, then `cd` into it. Then run:

```bash
pip install -e .
```

## Usage

### Command line

Convert CSV or XLSX of sequences to a FASTA file (info header goes to `stdout`).

```bash
$ printf 'name\tseq\tdata\nSeq1\tAAAAA\tSome info\n' | table2fasta -n name -s seq -d data
Generating FASTA from tables with the following parameters:
        input: <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>
        sequence: seq
        name: ['name']
        description: ['data']
        worksheet: Sheet 1
        output: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
WARNING: file extension "" is not recognised. Defaulting to .tsv

>Seq1 data=Some_info
AAAAA
```

Convert GFF tables to TSV (or CSV).

```bash
$ printf 'test_seq\ttest_source\tgene\t1\t10\t.\t+\t.\tID=test01;attr1=+\n' | gff2table 
Converting GFF with the following parameters:
        input: <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>
        format: TSV
        metadata: False
        output: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
seqid   source  feature start   end     score   strand  phase   ID      attr1
test_seq        test_source     gene    1       10      .       +       .       test01  +

$ printf 'test_seq\ttest_source\tgene\t1\t10\t.\t+\t.\tID=test01;attr1=+\n' | gff2table -f CSV
Converting GFF with the following parameters:
        input: <_io.TextIOWrapper name='<stdin>' mode='r' encoding='utf-8'>
        format: CSV
        metadata: False
        output: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>
seqid,source,feature,start,end,score,strand,phase,ID,attr1
test_seq,test_source,gene,1,10,.,+,.,test01,+
```

### Detailed usage

```
$ table2fasta --help
usage: table2fasta [-h] [--sequence SEQUENCE] --name [NAME ...] [--description [DESCRIPTION ...]] [--worksheet WORKSHEET] [--output OUTPUT] [input]

Convert a CSV or XLSX of sequences to a FASTA file.

positional arguments:
  input                 Input file in TSV, CSV, or XLSX format. Default STDIN.

options:
  -h, --help            show this help message and exit
  --sequence SEQUENCE, -s SEQUENCE
                        Column to take sequence from. Default "sequence"
  --name [NAME ...], -n [NAME ...]
                        Column(s) to take sequence name from. Concatenates values with "_", replaces spaces with "-". Required.
  --description [DESCRIPTION ...], -d [DESCRIPTION ...]
                        Column(s) to take sequence description from. Concatenates values with ";", replaces spaces with "_". Default: don't use.
  --worksheet WORKSHEET, -w WORKSHEET
                        For XLSX files, the worksheet to take the table from. Default "Sheet 1"
  --output OUTPUT, -o OUTPUT
                        Output file. Default STDOUT
```

```
$ gff2table --help
usage: gff2table [-h] [--format {TSV,CSV}] [--metadata] [--output OUTPUT] [input]

Convert a GFF to a TSV file.

positional arguments:
  input                 Input file in GFF format. Default STDIN.

options:
  -h, --help            show this help message and exit
  --format {TSV,CSV}, -f {TSV,CSV}
                        File format. Default TSV
  --metadata, -m        Write GFF header as commented lines.
  --output OUTPUT, -o OUTPUT
                        Output file. Default STDOUT
```

### Python API

#### FASTA

Read FASTA files (or strings) into iterators of named tuples.

```python
>>> list(read_fasta('''
... >example This is a description
... ATCG
... '''))
[FastaSequence(name='example', description='This is a description', sequence='ATCG')]
```

These named tuples show as FASTA format when printed.

```python
>>> s = FastaSequence("example", "This is a description", "ATCG")
>>> print(s)
>example This is a description
ATCG

```

And can be written to a file (default `stdout`):

```python
>>> fasta_stream = [FastaSequence("example", "This is a description", 
...                               "ATCG"),
...                 FastaSequence("example2", "This is another sequence", 
...                               "GGGAAAA")]
>>> write_fasta(fasta_stream) 
>example This is a description
ATCG
>example2 This is another sequence
GGGAAAA

```

#### GFF

Makes an attempt to conform to GFF3 but makes no guarantees.

Similar to the FSAT utiities, GFF is read into named tuples.

```python
>>> list(read_gff('''
...     ##meta1 item1
...     #meta2  item2   comment
...     test_seq    test_source gene    1   10  .   +   .   ID=test01;attr1=+
...     test_seq    test_source gene    9   100  .   +   .   Parent=test01;attr2=+
...     '''))
[GffLine(metadata=[GffMetadatum(name='meta1 item1', flag='constrained', values=()), GffMetadatum(name='meta2  item2   comment', flag='free', values=())], columns=GffColumns(seqid='test_seq', source='test_source', feature='gene', start=1, end=10, score='.', strand='+', phase='.'), attributes={'ID': 'test01', 'attr1': '+'}), GffLine(metadata=[GffMetadatum(name='meta1 item1', flag='constrained', values=()), GffMetadatum(name='meta2  item2   comment', flag='free', values=())], columns=GffColumns(seqid='test_seq', source='test_source', feature='gene', start=9, end=100, score='.', strand='+', phase='.'), attributes={'Parent': 'test01', 'attr2': '+'})]

```

These render as GFF lines when printed.

```python
>>> metadata = [("meta1", "constrained", {"item1": []}), 
...             ("meta2", "free", {"item2": ["comment"]})]
>>> seqid, source_id = "test_seq", "test_source"
>>> print(GffLine(metadata, 
...               GffColumns(seqid, source_id, "gene", 1, 10, ".", "+", "."), 
...               {"ID": "test01", "attr1": "+"})) 
test_seq        test_source     gene    1       10      .       +       .       ID=test01;attr1=+

```

#### GFF lookup table

An iterable of GFFLines can be converted into a lookup table mapping
chromosome location to feature annotations. Regions without annotation
are automatically filled with references to upstream or 
downstream features.

Just use the `lookup_table` function on an iterable of `GffLine` objects,
such as that produced by `read_gff`.

But there are currently some limitations:
- Currently only works for single-chromosome files.
- Only references parent features. Child features not yet indexed.
- Will not work for GFFs with a single parent feature.
- Ignores the following feature types: "region", :repeat_region"

#### Interconversion

GFFLines can be converted to dictionaries and vice versa.

```python
>>> d = dict(seqid='TEST', source='test', feature='gene', start=1, end=100, score='.', strand='+', phase='+')
>>> print(dict2gff(d)) 
TEST        test    gene    1       100     .       +       +
>>> print(dict2gff(d | dict(ID='test001', comment='This is a test'))) 
TEST    test    gene    1       100     .       +       +       ID=test001;comment=This is a test
```

```python
>>> line = "TEST    test    gene    1       100     .       +       +       ID=test001;comment=Test"
>>> list(gff2dict(read_gff(line)))
[{'seqid': 'TEST', 'source': 'test', 'feature': 'gene', 'start': 1, 'end': 100, 'score': '.', 'strand': '+', 'phase': '+', 'ID': 'test001', 'comment': 'Test'}]    

```

And Pandas daatFrames can be converted to FASTA.

```python
 >>> import pandas as pd
>>> df = pd.DataFrame(dict(seq=['atcg', 'aaaa'], title=['seq1', 'seq2'], info=['Seq1', 'Seq1'], score=[1, 2]))
>>> df 
        seq title  info  score
0  atcg  seq1  Seq1      1
1  aaaa  seq2  Seq1      2
>>> list(df2fasta(df, sequence='seq', names=['title'], descriptions=['info', 'score']))
[FastaSequence(name='seq1', description='info=Seq1;score=1', sequence='atcg'), FastaSequence(name='seq2', description='info=Seq1;score=2', sequence='aaaa')]
```

## Documentation

Check the API [here](https://bioino.readthedocs.org).