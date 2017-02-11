from itertools import chain

from .data import CHARACTERS_LOOKUP, SWITCH_CODES, Submode
from .util import switch_base, to_base, chunks


# -- Number compaction mode ----------------------------------------------------

def compact_numbers(data):
    """Encodes data into code words using the Numbers compaction mode.

    Can encode: Digits 0-9, ASCII
    Rate compaction: 2.9 bytes per code word
    """
    def compact_chunk(chunk):
        number = "".join([chr(x) for x in chunk])
        value = int("1" + number)
        return to_base(value, 900)

    compacted_chunks = [compact_chunk(chunk) for chunk in chunks(data, size=44)]

    return chain(*compacted_chunks)


# -- Text compaction mode ------------------------------------------------------

def compact_text_interim(data):

    def exists_in_submode(char, submode):
        return char in CHARACTERS_LOOKUP and \
               submode in CHARACTERS_LOOKUP[char]

    def get_submode(char):
        if char not in CHARACTERS_LOOKUP:
            raise ValueError("Cannot encode char: {}".format(char))

        submodes = CHARACTERS_LOOKUP[char].keys()

        preference = [Submode.LOWER, Submode.UPPER, Submode.MIXED, Submode.PUNCT]

        for submode in preference:
            if submode in submodes:
                return submode

        raise ValueError("Cannot encode char: {}".format(char))

    # By default, encoding starts with uppercase submode
    submode = Submode.UPPER

    codes = []

    for char in data:
        # Do we need to switch submode?
        # TODO: use one-character switches
        if not exists_in_submode(char, submode):
            prev_submode = submode
            submode = get_submode(char)

            switch_codes = SWITCH_CODES[prev_submode][submode]
            codes.extend(switch_codes)

        codes.append(CHARACTERS_LOOKUP[char][submode])

    return codes

def compact_text(data):
    """Encodes data into code words using the Text compaction mode.

    Can encode: ASCII 9, 10, 13 and 32-126
    Rate compaction: 2 bytes per code word
    """

    # Since each code word consists of 2 characters, a padding value is
    # needed when encoding a single character. 29 is used as padding because
    # it's a switch in all 4 submodes, and doesn't add any data.
    PADDING_INTERIM_CODE = 29

    def compact_chunk(chunk):
        if len(chunk) == 1:
            chunk.append(PADDING_INTERIM_CODE)

        return 30 * chunk[0] + chunk[1]

    interim_codes = compact_text_interim(data)

    return [compact_chunk(chunk) for chunk in chunks(interim_codes, 2)]


# -- Bytes compaction mode -----------------------------------------------------

def compact_bytes(data):
    """Encodes data into code words using the Byte compaction mode.

    Can encode: ASCII 0 to 255
    Rate compaction: 1.2 byte per code word
    """

    def compact_chunk(chunk):
        return compact_full_chunk(chunk) if len(chunk) == 6 \
            else compact_incomplete_chunk(chunk)

    def compact_full_chunk(chunk):
        """Encodes a chunk consisting of exactly 6 bytes.

        The chunk is encoded to 5 code words by changing the base from 256 to 900.
        """

        digits = [i for i in chunk]
        return switch_base(digits, 256, 900)

    def compact_incomplete_chunk(chunk):
        """Encodes a chunk consisting of less than 6 bytes.

        The chunk is encoded to 6 code words leaving the base unchanged.
        """
        return [i for i in chunk]

    compacted_chunks = [compact_chunk(chunk) for chunk in chunks(data, size=6)]

    return chain(*compacted_chunks)


# -- Bringing it all together --------------------------------------------------

def compact(data):
    """Encodes given data into an array of PDF417 code words."""

    def compact_chunks(chunks):
        compacted_chunks = [compact_chunk(ordinal, *args) for ordinal, args in enumerate(chunks)]

        return chain(*compacted_chunks)

    def compact_chunk(ordinal, chunk, compact_fn):
        code_words = []

        # Add the switch code if required
        add_switch_code = ordinal > 0 or compact_fn != compact_text
        if add_switch_code:
            code_words.append(get_switch_code(compact_fn, chunk))

        code_words.extend(compact_fn(chunk))

        return code_words

    def split_to_chunks(data):
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

    chunks = split_to_chunks(data)
    return compact_chunks(chunks)


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
