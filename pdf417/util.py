from __future__ import division


def from_base(digits, base):
    return sum([v * (256 ** (len(digits) - k - 1)) for k, v in enumerate(digits)])


def to_base(value, base):
    digits = []

    while value > 0:
        digits.insert(0, value % base)
        value //= base

    return digits


def switch_base(digits, source_base, target_base):
    return to_base(from_base(digits, source_base), target_base)
