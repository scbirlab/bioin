"""Utilities for working with tables."""

from typing import Callable

from io import TextIOWrapper
import sys
import os
from functools import partial

from carabiner.decorators import vectorize
from pandas import DataFrame, read_csv, read_excel

_FILE_TYPES = {
    '.xlsx': read_excel,
    '.csv': partial(read_csv, sep=','),
    '.tsv': partial(read_csv, sep='\s+'),
    '.txt': partial(read_csv, sep='\s+')
}


def _sniff_format(f: TextIOWrapper) -> Callable[[TextIOWrapper], DataFrame]:

    loader = None
    _, file_suffix = os.path.splitext(f.name)
    file_suffix = file_suffix.lower()
    default = '.tsv'

    try:

        loader = _FILE_TYPES[file_suffix]

    except KeyError:

        print(f'WARNING: file extension "{file_suffix}" is not recognised.',
              f'Defaulting to {default}\n', 
              file=sys.stderr)
        loader = _FILE_TYPES[default]

    return loader


@vectorize
def _sanitize_columns(x: str) -> str:

    return x.replace(' ', '_').replace('(', '').replace(')', '')


def _load_table(f: TextIOWrapper, 
                reader: Callable[[TextIOWrapper], DataFrame] = read_csv, 
                worksheet: int = 0) -> DataFrame:

    data_string = f
    
    try:
        data = reader(data_string, 
                      sheet_name=worksheet)
    except TypeError:
        data = reader(data_string)

    data.columns = list(_sanitize_columns(data.columns))

    return data
