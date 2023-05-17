"""Utilities for bioin package."""

from collections.abc import Callable, Mapping

def prettyprint_dict(x: Mapping,
                     message: str,
                     output: Callable[[str], None]):

    key_val_str = [f'{key}: {val}' for key, val in x.items()]

    output(message + '\n\t{}\n'.format('\n\t'.join(key_val_str)))