import pytest

from pdf417gen.compaction import compact, compact_bytes, compact_numbers, compact_text
from pdf417gen.compaction import optimizations, _split_to_chunks, Chunk
from pdf417gen.compaction.text import compact_text_interim
from pdf417gen.encoding import to_bytes
from pdf417gen.data import SWITCH_CODE_LOOKUP
from pdf417gen.types import Submode


def test_byte_compactor():
    def do_compact(str):
        return list(compact_bytes(to_bytes(str)))

    assert do_compact("alcool") == [163, 238, 432, 766, 244]
    assert do_compact("alcoolique") == [163, 238, 432, 766, 244, 105, 113, 117, 101]
    assert do_compact("\00alc\00l") == [0, 573, 880, 505, 712]

def test_text_compactor_interim():
    def do_compact(str):
        return list(compact_text_interim(to_bytes(str)))

    # Latch codes for single-code transitions
    lm = SWITCH_CODE_LOOKUP[Submode.LOWER][Submode.MIXED]
    ul = SWITCH_CODE_LOOKUP[Submode.UPPER][Submode.LOWER]
    um = SWITCH_CODE_LOOKUP[Submode.UPPER][Submode.MIXED]
    ml = SWITCH_CODE_LOOKUP[Submode.MIXED][Submode.LOWER]
    mu = SWITCH_CODE_LOOKUP[Submode.MIXED][Submode.UPPER]
    mp = SWITCH_CODE_LOOKUP[Submode.MIXED][Submode.PUNCT]
    pu = SWITCH_CODE_LOOKUP[Submode.PUNCT][Submode.UPPER]

    # Upper transitions
    assert do_compact("Ff") == [5, ul, 5]
    assert do_compact("F#") == [5, um, 15]
    assert do_compact("F!") == [5, um, mp, 10]

    # Lower transitions
    assert do_compact("fF") == [ul, 5, lm, mu, 5]
    assert do_compact("f#") == [ul, 5, lm, 15]
    assert do_compact("f!") == [ul, 5, lm, mp, 10]

    # Mixed transitions
    assert do_compact("#f") == [um, 15, ml, 5]
    assert do_compact("#F") == [um, 15, mu, 5]
    assert do_compact("#!") == [um, 15, mp, 10]

    # Punct transitions
    assert do_compact("!f") == [um, mp, 10, pu, ul, 5]
    assert do_compact("!F") == [um, mp, 10, pu, 5]
    assert do_compact("!#") == [um, mp, 10, pu, um, 15]


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
    # Use 13 digites to avoid optimization which keeps it in text mode
    assert do_compact("ABC1234567890123") == [
        1, 89, 902, 17, 110, 836, 811, 223
    ]

    # When starting with numbers, we do need to switch
    assert do_compact("1234567890123ABC") == [
        902, 17, 110, 836, 811, 223,
        900, 1, 89
    ]

    # Also with bytes
    assert do_compact(b"\x0B") == [901, 11]

    # Alternate bytes switch code when number of bytes is divisble by 6
    assert do_compact(b"\x0B\x0B\x0B\x0B\x0B\x0B") == [924, 18, 455, 694, 754, 291]


def test_compact_force_binary_text():
    """Test that force_binary=True correctly handles text data."""
    def do_compact(data, force=False):
        return list(compact(to_bytes(data), force_binary=force))
    
    # Text that would normally use text compaction
    text_data = "HelloWorld"
    text_normal = do_compact(text_data)
    text_forced = do_compact(text_data, force=True)
    
    # Normal should use text compaction (no byte switch)
    assert 901 not in text_normal[:1]  # No BYTE_LATCH at start
    assert 924 not in text_normal[:1]  # No BYTE_LATCH_ALT at start
    
    # Forced binary should start with byte latch
    assert text_forced[0] in (901, 924)


def test_compact_force_binary_numeric():
    """Test that force_binary=True correctly handles numeric data."""
    def do_compact(data, force=False):
        return list(compact(to_bytes(data), force_binary=force))
    
    # Numeric data that would normally use numeric compaction
    num_data = "1234567890"
    num_normal = do_compact(num_data)
    num_forced = do_compact(num_data, force=True)
    
    # Normal should use numeric compaction (902)
    assert num_normal[0] == 902
    
    # Forced binary should use byte compaction
    assert num_forced[0] in (901, 924)

def test_compact_force_binary_already_binary():
    """Test that force_binary=True correctly handles binary data."""
    def do_compact(data, force=False):
        if isinstance(data, str):
            data = to_bytes(data)
        return list(compact(data, force_binary=force))
    
    # Binary data (would use byte compaction either way)
    binary_data = b"\x01\x02\x03\x04\x05"
    bin_normal = do_compact(binary_data)
    bin_forced = do_compact(binary_data, force=True)
    
    # Both should start with byte latch
    assert bin_normal[0] in (901, 924)
    assert bin_forced[0] in (901, 924)
    
    # Should be identical since both use byte compaction
    assert bin_normal == bin_forced

@pytest.mark.parametrize("data,expected", [
    ('aabb1122foobar💔', [
        ('aabb', compact_text),
        ('1122', compact_numbers),
        ('foobar', compact_text),
        ('💔', compact_bytes),
    ]),
])
def test_split_to_chunks(data, expected):
    data = to_bytes(data)
    expected = [Chunk(text.encode(), fn) for text, fn in expected]
    assert list(_split_to_chunks(data)) == expected


@pytest.mark.parametrize("data,expected", [
    # Don't switch to text mode for chunks shorter than 13 numeric chars
    # if bordering text chunk
    ('foo1234567890bar', [
        ('foo1234567890bar', compact_text),
    ]),
    ('1234567890bar', [
        ('1234567890bar', compact_text),
    ]),
    ('foo1234567890', [
        ('foo1234567890', compact_text),
    ]),
    ('foo1234567890💔', [
        ('foo1234567890', compact_text),
        ('💔', compact_bytes),
    ]),
    ('💔1234567890foo', [
        ('💔', compact_bytes),
        ('1234567890foo', compact_text),
    ]),

    # Switch for 13+ chars or when not bordering text chunk
    ('foo1234567890123bar', [
        ('foo', compact_text),
        ('1234567890123', compact_numbers),
        ('bar', compact_text),
    ]),
    ('1234567890', [
        ('1234567890', compact_numbers),
    ]),
    ('💔1234567890💔', [
        ('💔', compact_bytes),
        ('1234567890', compact_numbers),
        ('💔', compact_bytes),
    ]),
])
def test_optimizations(data, expected):
    def chars(string):
        return [i for i in to_bytes(string)]

    data = to_bytes(data)
    expected = [Chunk(text.encode(), fn) for text, fn in expected]

    actual = _split_to_chunks(data)
    actual = optimizations.replace_short_numeric_chunks(actual)
    actual = optimizations.merge_chunks_with_same_compact_fn(actual)

    assert list(actual) == expected
