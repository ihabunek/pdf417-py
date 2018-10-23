import pytest

from pdf417gen.encoding import to_bytes
from pdf417gen.compaction import (
    compact, compact_bytes, compact_numbers, compact_text, compact_text_interim)


def test_byte_compactor():
    def do_compact(str):
        return list(compact_bytes(to_bytes(str)))

    assert do_compact("alcool") == [163, 238, 432, 766, 244]
    assert do_compact("alcoolique") == [163, 238, 432, 766, 244, 105, 113, 117, 101]


def test_text_compactor_interim():
    def do_compact(str):
        return list(compact_text_interim(to_bytes(str)))

    # Upper transitions
    assert do_compact("Ff") == [5, 27, 5]
    assert do_compact("F#") == [5, 28, 15]
    assert do_compact("F!") == [5, 28, 25, 10]

    # Lower transitions
    assert do_compact("fF") == [27, 5, 28, 28, 5]
    assert do_compact("f#") == [27, 5, 28, 15]
    assert do_compact("f!") == [27, 5, 28, 25, 10]


# Bug where the letter g would be encoded as " in the PUNCT submode
# https://github.com/ihabunek/pdf417-py/issues/8
def test_text_compactor_interim_error_letter_g():
    def do_compact(str):
        return list(compact_text_interim(to_bytes(str)))

    assert do_compact(">g") == [
        28,  # switch to MIXED
        25,  # switch to PUNCT
        2,   # Encode >"
        29,  # switch to UPPER
        27,  # switch to LOWER
        6,   # encode g
    ]


def test_text_compactor():
    def do_compact(str):
        return list(compact_text(to_bytes(str)))

    assert do_compact("Super ") == [567, 615, 137, 809]
    assert do_compact("Super !") == [567, 615, 137, 808, 760]


def test_numbers_compactor():
    numbers = [ord(x) for x in "01234"]
    assert list(compact_numbers(numbers)) == [112, 434]


def test_compact():
    def do_compact(str):
        return list(compact(to_bytes(str)))

    # When starting with text, the first code word does not need to be the switch
    assert do_compact("ABC123") == [1, 89, 902, 1, 223]

    # When starting with numbers, we do need to switch
    assert do_compact("123ABC") == [902, 1, 223, 900, 1, 89]

    # Also with bytes
    assert do_compact(b"\x0B") == [901, 11]

    # Alternate bytes switch code when number of bytes is divisble by 6
    assert do_compact(b"\x0B\x0B\x0B\x0B\x0B\x0B") == [924, 18, 455, 694, 754, 291]


VARIANTS = (
    (
        '7789777004000951 388044',
        [902, 30, 114, 386, 259, 234, 351, 900, 808, 98, 240, 124],
    ),
    (
        '12345678901234 aaaaa 1111',
        [902, 171, 209, 269, 12, 434, 900, 807, 0, 0, 26, 841, 31, 59],
    ),
    (
        "hello12345678901234world",
        [817, 131, 344, 902, 171, 209, 269, 12, 434, 900, 832, 437, 333],
    ),
    (
        "hello123456789012world",
        [817, 131, 344, 841, 63, 125, 187, 249, 1, 89, 900, 832, 437, 333],
    ),
    (
        "12345678901234 109876543210123 123 123 123",
        [902, 171, 209, 269, 12, 434, 900, 809, 902, 1, 791, 564, 354, 522, 323,
         900, 808, 32, 119, 900, 808, 32, 119, 900, 808, 32, 119]
    ),
    (
        "\x0B3333\x0B3333",
        [901, 11, 900, 843, 93, 119, 901, 11, 900, 843, 93, 119]
    ),
)


@pytest.mark.parametrize("data,expected", VARIANTS)
def test_numeric_compaction(data, expected):
    def do_compact(str):
        return list(compact(to_bytes(str), numeric_compaction=True))

    assert do_compact(data) == expected
