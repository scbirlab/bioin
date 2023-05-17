"""Utilities for working with tables."""

from typing import Callable, IO, Sequence
import sys
import os
from functools import partial
import pandas as pd

_FILE_TYPES = {
    '.xlsx': pd.read_excel,
    '.csv': partial(pd.read_csv, sep=','),
    '.tsv': partial(pd.read_csv, sep='\t'),
    '.txt': partial(pd.read_csv, sep='\t')
}


def _sniff_format(f: IO) -> Callable[[IO], pd.DataFrame]:

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


def _sanitize_columns(x: Sequence[str]) -> Sequence[str]:

    return [col.replace(' ', '_').replace('(', '').replace(')', '') 
            for col in x]


def _load_table(f: IO, 
                reader: Callable[[IO], pd.DataFrame] = pd.read_csv, 
                worksheet: int = 0) -> pd.DataFrame:

    data_string = f
    
    try:
        data = reader(data_string, 
                      sheet_name=worksheet)
    except TypeError:
        data = reader(data_string)

    data.columns = _sanitize_columns(data)

    return data
