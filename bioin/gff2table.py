"""Command-line utility for converting GFF files to comma- or tab-delimited files."""

import argparse
import sys

from . import gff, utils


def main() -> None:

    parser = argparse.ArgumentParser(description='Convert a GFF to a TSV file.')
    parser.add_argument('input', 
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        nargs='?',
                        help='Input file in GFF format. Default STDIN.')
    parser.add_argument('--format', '-f', 
                        type=str,
                        default='TSV',
                        choices=['TSV', 'CSV'],
                        help='File format. Default %(default)s')
    parser.add_argument('--metadata', '-m', 
                        action='store_true',
                        help='Write GFF header as commented lines.')
    parser.add_argument('--output', '-o', 
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Output file. Default STDOUT')

    args = parser.parse_args()

    utils.prettyprint_dict(vars(args),
                           'Converting GFF with the following parameters:',
                           sys.stderr.write)

    separator = dict(TSV='\t', CSV=',')
    
    try:

        gff.gff2csv(gff.read_gff(args.input), 
                    args.output,
                    write_metadata=args.metadata,
                    sep=separator[args.format])

    except BrokenPipeError:

        pass

    return None


if __name__ == '__main__':

    main()
