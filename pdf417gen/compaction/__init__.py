from itertools import chain

from pdf417gen.compaction.byte import compact_bytes
from pdf417gen.compaction.numeric import compact_numbers
from pdf417gen.compaction.text import compact_text
from pdf417gen.data import CHARACTERS_LOOKUP


def compact(data):
    """Encodes given data into an array of PDF417 code words."""
    chunks = _split_to_chunks(data)
    return _compact_chunks(chunks)


def _compact_chunks(chunks):
    compacted_chunks = [_compact_chunk(ordinal, *args) for ordinal, args in enumerate(chunks)]

    return chain(*compacted_chunks)


def _compact_chunk(ordinal, chunk, compact_fn):
    code_words = []

    # Add the switch code if required
    add_switch_code = ordinal > 0 or compact_fn != compact_text
    if add_switch_code:
        code_words.append(get_switch_code(compact_fn, chunk))

    code_words.extend(compact_fn(chunk))

    return code_words


def _split_to_chunks(data):
    """Splits a string into chunks which can be encoded with the same encoder.

    Implemented as a generator which yields chunks and the appropriate encoder.

    TODO: Currently always switches to the best encoder, even if it's just
    for one character, consider a better algorithm.
    """

    # Default compaction mode is Text (does not require an initial switch code)
    function = compact_text
    chunk = []

    for char in data:
        new_function = get_optimal_compactor_fn(char)
        if function != new_function:
            if chunk:
                yield chunk, function

            chunk = []
            function = new_function
        chunk.append(char)

    if chunk:
        yield chunk, function


def get_optimal_compactor_fn(char):
    if 48 <= char <= 57:
        return compact_numbers

    if char in CHARACTERS_LOOKUP:
        return compact_text

    return compact_bytes


def get_switch_code(compact_fn, data):
    TEXT = 900
    BYTES = 901
    BYTES_ALT = 924
    NUMBERS = 902

    if compact_fn == compact_text:
        return TEXT

    if compact_fn == compact_bytes:
        return BYTES_ALT if len(data) % 6 == 0 else BYTES

    if compact_fn == compact_numbers:
        return NUMBERS

    assert False, "Nonexistant compaction function"
