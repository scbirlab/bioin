"""Command-line utility for converting comma- or tab-delimited files 
or XLSX to FASTA format.
"""

from collections.abc import Generator
import argparse
import sys
import pandas as pd

from .fasta import FastaSequence, write_fasta
from .tables import _load_table, _sanitize_columns, _sniff_format
from .utils import prettyprint_dict


def df2fasta(data: pd.DataFrame, 
             sequence: str,
             names: list, 
             descriptions: list = [],
             namesep: str = '_',
             descsep: str = ';') -> Generator[FastaSequence]:
    
    """Make a FASTA stream from a Pandas DataFrame.

    The FASTA sequence is taken from the `sequence` column, and the names is taken from the
    `names` columns, concatenated separated by `namesep`. If provided, description columns values
    are added to the descriptio n field as 'key=value' pairs, separated by `descsep`.

    Parameters
    ----------
    data : pd.DataFrame
        Input data. Must contain columns named as `sequence`, `names`, and (optionally) `descriptions`.
    sequence : str
        Name of column containing sequences.
    names :  list
        Names of columns to use as sequence names in FASTA. 
    descriptions :  list, optional
        Names of columns to add as metadata to the description in FASTA. 
    namesep : str, optional
        Separator between name values. Default: '_'.
    descsep : str, optional
        Separator between description values. Default: ';'.

    Yields
    ------
    FastaSequence
        Object representing a single FASTA sequence.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame(dict(seq=['atcg', 'aaaa'], title=['seq1', 'seq2'], info=['Seq1', 'Seq1'], score=[1, 2]))
    >>> df  # doctest: +NORMALIZE_WHITESPACE
            seq title  info  score
    0  atcg  seq1  Seq1      1
    1  aaaa  seq2  Seq1      2
    >>> list(df2fasta(df, sequence='seq', names=['title'], descriptions=['info', 'score']))  # doctest: +NORMALIZE_WHITESPACE
    [FastaSequence(name='seq1', description='info=Seq1;score=1', sequence='atcg'), FastaSequence(name='seq2', description='info=Seq1;score=2', sequence='aaaa')]
    >>> list(df2fasta(df, sequence='seq', names=['title', 'info'], descriptions=['score']))  # doctest: +NORMALIZE_WHITESPACE
    [FastaSequence(name='seq1_Seq1', description='score=1', sequence='atcg'), FastaSequence(name='seq2_Seq1', description='score=2', sequence='aaaa')]

    """

    names, descriptions, [sequence] = (_sanitize_columns(item) 
                                       for item in (names, descriptions, [sequence]))
    columns = names + descriptions + [sequence]

    cols_in_data = [column in data for column in columns]
    cols_not_in_data = [column for column in columns if column not in data]

    if not all(cols_in_data):
        
        raise KeyError('Some requested columns not in the table: '
                       '"{}"'.format('", "'.join(cols_not_in_data)))
    
    data = data[columns]

    for row in data.itertuples():

        name = namesep.join(str(getattr(row, name)).replace(' ', '-') 
                            for name in names)
        decription = descsep.join('{}={}'.format(desc, 
                                                 str(getattr(row, desc)).replace(' ', '_')) 
                              for desc in descriptions)
        seq = getattr(row, sequence)

        yield FastaSequence(name, decription, seq)
    

def main() -> None:

    parser = argparse.ArgumentParser(description='''
    Convert a CSV or XLSX of sequences to a FASTA file.
    ''')
    parser.add_argument('input', 
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        nargs='?',
                        help='Input file in TSV, CSV, or XLSX format. Default STDIN.')
    parser.add_argument('--sequence', '-s', 
                        type=str, 
                        default='sequence',
                        help='Column to take sequence from. Default "%(default)s"')
    parser.add_argument('--name', '-n', 
                        nargs='*',
                        type=str,
                        required=True,
                        help='Column(s) to take sequence name from. '
                             'Concatenates values with "_", '
                             'replaces spaces with "-". Required.')
    parser.add_argument('--description', '-d', 
                        nargs='*',
                        type=str, 
                        default=[],
                        help='Column(s) to take sequence description from. '
                             'Concatenates values with ";", '
                             'replaces spaces with "_". Default: don\'t use.')
    parser.add_argument('--worksheet', '-w', 
                        type=str, default='Sheet 1',
                        help='For XLSX files, the worksheet to take the table from. Default "%(default)s"')
    parser.add_argument('--output', '-o', 
                        dest='output', 
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Output file. Default STDOUT')

    args = parser.parse_args()

    prettyprint_dict(vars(args),
                     'Generating FASTA from tables with the following parameters:',
                     sys.stderr.write)

    table = _load_table(args.input, 
                        reader=_sniff_format(args.input), 
                        worksheet=args.worksheet)
    
    fasta_stream = df2fasta(table, 
                            sequence=args.sequence,
                            names=args.name, 
                            descriptions=args.description)

    try:
        write_fasta(fasta_stream,
                    file=args.output)
    except BrokenPipeError:
        pass

    return None


if __name__ == '__main__':

    main()