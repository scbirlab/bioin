"""Utilities for working with tables."""

from carabiner.decorators import vectorize

@vectorize
def _sanitize_columns(x: str) -> str:

    return x.replace(' ', '_').replace('(', '').replace(')', '')
