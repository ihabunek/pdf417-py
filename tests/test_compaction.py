from pdf417.compaction import compact, compact_bytes, compact_numbers, compact_text, compact_text_interim


# def test_byte_encoder_can_encode():
#     enc = ByteEncoder()
#     # Can encode any byte from 0 to 255
#     for x in range(0, 255):
#         assert enc.can_encode(chr(x))



def test_byte_compactor():
    assert list(compact_bytes("alcool")) == [163, 238, 432, 766, 244]
    assert list(compact_bytes("alcoolique")) == [163, 238, 432, 766, 244, 105, 113, 117, 101]


# def test_text_encoder_can_encode():
#     enc = TextEncoder()
#     # Can encode ASCII 9, 10, 13, 32, 33 and 35-126
#     # TODO: should be able to encode double quote (ASCII 34), but doesn't currently
#     for x in range(0, 255):
#         can_encode = x in [9, 10, 13, 32, 33] or x in range(35, 127)
#         assert enc.can_encode(chr(x)) == can_encode


def test_text_compactor_interim():
    # Upper transitions
    assert compact_text_interim("Ff") == [5, 27, 5]
    assert compact_text_interim("F#") == [5, 28, 15]
    assert compact_text_interim("F!") == [5, 28, 25, 10]

    # Lower transitions
    assert compact_text_interim("fF") == [27, 5, 28, 28, 5]
    assert compact_text_interim("f#") == [27, 5, 28, 15]
    assert compact_text_interim("f!") == [27, 5, 28, 25, 10]


def test_text_compactor():
    assert compact_text("Super ") == [567, 615, 137, 809]
    assert compact_text("Super !") == [567, 615, 137, 808, 760]


def test_numbers_compactor():
    assert list(compact_numbers("01234")) == [112, 434]


def test_compact():
    # When starting with text, the first code word does not need to be the switch
    assert list(compact("ABC123")) == [1, 89, 902, 1, 223]

    # When starting with numbers, we do need to switch
    assert list(compact("123ABC")) == [902, 1, 223, 900, 1, 89]

    # Also with bytes
    assert list(compact("\x0B")) == [901, 11]

    # Alternate bytes switch code when number of bytes is divisble by 6
    assert list(compact("\x0B\x0B\x0B\x0B\x0B\x0B")) == [924, 18, 455, 694, 754, 291]
