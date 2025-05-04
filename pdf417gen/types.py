from enum import Enum, auto
from typing import Callable, Iterable, List, NamedTuple


Codeword = int
"""Codeword is an unit of data in the barcode encoded in base 929.
Codewords are represented as integers between 0 and 928."""

Barcode = List[List[int]]
"""Barcode is a sequence of codewords represented as low level code words ready to render."""

CompactionFn = Callable[[bytes], Iterable[Codeword]]
"""A function used to convert bytes into codewords"""


class Chunk(NamedTuple):
    """A chunk of barcode data with accompanying compaction function.

    All `data` must be supported by the `compact_fn`.
    """

    data: bytes
    compact_fn: CompactionFn


class Submode(Enum):
    """Text compaction sub-modes"""
    UPPER = auto()
    LOWER = auto()
    MIXED = auto()
    PUNCT = auto()
