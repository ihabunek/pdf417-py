from builtins import range
from pdf417.util import switch_base


class Encoder(object):

    def can_encode(self, char):
        """Checks whether the given character can be encoded using this encoder."""
        raise NotImplementedError()

    def get_switch_code(self, data):
        """Returns the switch code word for the encoding mode implemented by the encoder."""
        raise NotImplementedError()

    def encode(self, data, add_switch_code):
        """Encodes a string into codewords."""
        raise NotImplementedError()


class ByteEncoder(object):
    # Code word used to switch to Byte mode
    SWITCH_CODE_WORD = 901

    # Alternate code word used to switch to Byte mode; used when number of bytes
    # to encode is divisible by 6.
    SWITCH_CODE_WORD_ALT = 924

    def can_encode(self, char):
        """Byte encoder can encode any one character"""
        return True

    def get_switch_code(self, data):
        return self.SWITCH_CODE_WORD_ALT if len(data) % 6 == 0 \
            else self.SWITCH_CODE_WORD

    def chunks(self, data, size=6):
        """Generator which chunks data into 6 bytes batches"""
        for i in range(0, len(data), size):
            yield data[i:i+size]

    def encode(self, data, add_switch_code):
        code_words = []

        if add_switch_code:
            code_words.append(self.get_switch_code(data))

        # Encode in chunks of 6 bytes
        for chunk in self.chunks(data):
            code_words.extend(self.encode_chunk(chunk))

        return code_words

    def encode_chunk(self, chunk):
        return self.encode_full_chunk(chunk) if len(chunk) == 6 \
            else self.encode_incomplete_chunk(chunk)

    def encode_full_chunk(self, chunk):
        """Encodes a chunk consisting of exactly 6 bytes.

        The chunk is encoded to 5 code words by changing the base from 256 to 900.
        """
        digits = [ord(i) for i in chunk]
        return switch_base(digits, 256, 900)

    def encode_incomplete_chunk(self, chunk):
        """Encodes a chunk consisting of less than 6 bytes.

        The chunk is encoded to the same number of code words leaving the base unchanged.
        """
        return [ord(i) for i in chunk]
