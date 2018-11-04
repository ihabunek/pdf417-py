from __future__ import division

from builtins import bytes, str, zip
from itertools import tee, islice, chain


def from_base(digits, base):
    return sum(v * (base ** (len(digits) - k - 1)) for k, v in enumerate(digits))


def to_base(value, base):
    digits = []

    while value > 0:
        digits.insert(0, value % base)
        value //= base

    return digits


def switch_base(digits, source_base, target_base):
    return to_base(from_base(digits, source_base), target_base)


def chunks(iterable, size):
    """Generator which chunks data into chunks of given size."""
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, size))
        if not chunk:
            return
        yield chunk


def to_bytes(input, encoding='utf-8'):
    if isinstance(input, bytes):
        return bytes(input)

    if isinstance(input, str):
        return bytes(input, encoding)

    raise ValueError("Invalid input, expected string or bytes")


def iterate_prev_next(iterable):
    """
    Creates an iterator which provides previous, current and next item.
    """
    prevs, items, nexts = tee(iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)
