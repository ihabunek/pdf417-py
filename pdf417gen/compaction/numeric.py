"""
Numeric Compaction Mode (NC)

Can encode: Digits 0-9, ASCII
Rate compaction: 2.9 bytes per code word
"""

from itertools import chain
from typing import Iterable, List, Tuple
from pdf417gen.types import Codeword
from pdf417gen.util import to_base, chunks


def _compact_chunk(chunk: Tuple[int, ...]) -> List[Codeword]:
    number = "".join(chr(x) for x in chunk)
    value = int("1" + number)
    return to_base(value, 900)


def compact_numbers(data: bytes) -> Iterable[Codeword]:
    """Encodes data into code words using the Numeric compaction mode."""
    compacted_chunks = (_compact_chunk(chunk) for chunk in chunks(data, size=44))
    return chain(*compacted_chunks)
