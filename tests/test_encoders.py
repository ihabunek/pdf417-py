from pdf417.encoders import ByteEncoder


def test_byte_encoder_can_encode():
    enc = ByteEncoder()
    # Can encode any byte from 0 to 255
    for x in range(0, 255):
        assert enc.can_encode(chr(x)) == True

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
