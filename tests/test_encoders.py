from pdf417.compaction import ByteEncoder, TextEncoder, NumberEncoder, DataEncoder


def test_byte_encoder_can_encode():
    enc = ByteEncoder()
    # Can encode any byte from 0 to 255
    for x in range(0, 255):
        assert enc.can_encode(chr(x))


def test_byte_encoder_switch_code():
    enc = ByteEncoder()

    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("1")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("12")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("123")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("1234")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("12345")
    assert enc.SWITCH_CODE_WORD_ALT == enc.get_switch_code("123456")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("1234561")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("12345612")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("123456123")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("1234561234")
    assert enc.SWITCH_CODE_WORD == enc.get_switch_code("12345612345")
    assert enc.SWITCH_CODE_WORD_ALT == enc.get_switch_code("123456123456")


def test_byte_encoder():
    enc = ByteEncoder()

    assert enc.encode("alcool", True) == [924, 163, 238, 432, 766, 244]
    assert enc.encode("alcool", False) == [163, 238, 432, 766, 244]
    assert enc.encode("alcoolique", True) == [901, 163, 238, 432, 766, 244, 105, 113, 117, 101]
    assert enc.encode("alcoolique", False) == [163, 238, 432, 766, 244, 105, 113, 117, 101]


def test_text_encoder_can_encode():
    enc = TextEncoder()
    # Can encode ASCII 9, 10, 13, 32, 33 and 35-126
    # TODO: should be able to encode double quote (ASCII 34), but doesn't currently
    for x in range(0, 255):
        can_encode = x in [9, 10, 13, 32, 33] or x in range(35, 127)
        assert enc.can_encode(chr(x)) == can_encode


def test_text_encoder_encode_interim():
    enc = TextEncoder()

    # Upper transitions
    assert enc.encode_interim("Ff") == [5, 27, 5]
    assert enc.encode_interim("F#") == [5, 28, 15]
    assert enc.encode_interim("F!") == [5, 28, 25, 10]

    # Lower transitions
    assert enc.encode_interim("fF") == [27, 5, 28, 28, 5]
    assert enc.encode_interim("f#") == [27, 5, 28, 15]
    assert enc.encode_interim("f!") == [27, 5, 28, 25, 10]


def test_text_encoder_encode():
    enc = TextEncoder()

    assert enc.encode("Super ", True) == [900, 567, 615, 137, 809]
    assert enc.encode("Super ", False) == [567, 615, 137, 809]
    assert enc.encode("Super !", True) == [900, 567, 615, 137, 808, 760]
    assert enc.encode("Super !", False) == [567, 615, 137, 808, 760]


def test_numbers_encoder_encode():
    enc = NumberEncoder()

    assert enc.encode("01234", True) == [902, 112, 434]
    assert enc.encode("01234", False) == [112, 434]


def test_data_encoder_encode():
    enc = DataEncoder()

    # When starting with text, the first code word does not need to be the switch
    assert list(enc.encode("ABC123")) == [1, 89, 902, 1, 223]

    # When starting with numbers, we do need to switch
    assert list(enc.encode("123ABC")) == [902, 1, 223, 900, 1, 89]

    # Also with bytes
    assert list(enc.encode("\x0B")) == [901, 11]

    # Alternate bytes switch code when number of bytes is divisble by 6
    assert list(enc.encode("\x0B\x0B\x0B\x0B\x0B\x0B")) == [924, 18, 455, 694, 754, 291]
