import pytest

from pdf417gen.compaction import TEXT_LATCH, NUMERIC_LATCH
from pdf417gen.encoding import encode, encode_high, to_bytes, encode_macro

TEST_DATA = '\n'.join([
    'HRVHUB30',
    'HRK',
    '000000010000000',
    'Ivan Habunek',
    'Savska cesta 13',
    '10000 Zagreb',
    'Big Fish Software d.o.o.',
    'Savska cesta 13',
    '10000 Zagreb',
    'HR6623400091110651272',
    '00',
    'HR123456',
    'ANTS',
    'Razvoj paketa za bar kodove\n'
])


def test_encode_high():

    # High level encoding
    expected = [
        130, 227, 637, 601, 843, 25, 479, 227, 328, 765,

        NUMERIC_LATCH, 1, 624, 142, 113, 522, 200,

        TEXT_LATCH, 865, 479, 267, 630, 416, 868, 237, 1, 613, 130, 865, 479,
        567, 21, 550, 26, 64, 559, 26, 841, 115, 479, 841, 0, 0, 808, 777, 6,
        514, 58, 765, 871, 818, 206, 868, 177, 258, 236, 868, 567, 425, 592, 17,
        146, 118, 537, 448, 537, 448, 535, 479, 567, 21, 550, 26, 64, 559, 26,
        841, 115, 479, 841, 0, 0, 808, 777, 6, 514, 58, 765, 877, 539,

        NUMERIC_LATCH, 31, 251, 786, 557, 565, 1, 372,

        TEXT_LATCH, 865, 479, 840, 25, 479, 227, 841, 63, 125, 205, 479, 13,
        588, 865, 479, 537, 25, 644, 296, 450, 304, 570, 805, 26, 30, 536, 314,
        104, 634, 865, 479, 73, 714, 436, 412, 39, 661, 428, 120

    ]

    assert encode_high(to_bytes(TEST_DATA), 6, 2) == expected


def test_encode_low():

    # Low level encoding
    expected = [
        [130728, 119920, 82192, 93980, 67848, 99590, 66798, 110200, 128318, 260649],
        [130728, 129678, 101252, 127694, 75652, 113982, 97944, 129720, 129678, 260649],
        [130728, 86496, 66846, 104188, 106814, 96800, 93944, 102290, 119934, 260649],
        [130728, 128190, 73160, 96008, 102812, 67872, 115934, 73156, 119520, 260649],
        [130728, 120588, 104224, 129720, 129938, 119200, 81084, 101252, 120588, 260649],
        [130728, 125892, 113798, 88188, 71822, 129766, 108158, 113840, 120784, 260649],
        [130728, 85880, 120638, 66758, 119006, 96008, 66758, 120256, 85560, 260649],
        [130728, 128176, 128352, 99048, 123146, 128280, 115920, 110492, 128176, 260649],
        [130728, 129634, 99166, 67438, 81644, 127604, 67404, 111676, 85054, 260649],
        [130728, 107422, 91664, 121136, 73156, 78032, 79628, 99680, 107452, 260649],
        [130728, 119692, 125744, 107396, 85894, 70600, 123914, 70600, 119692, 260649],
        [130728, 129588, 77902, 105628, 67960, 113798, 88188, 71822, 107390, 260649],
        [130728, 82208, 120638, 108348, 117798, 120638, 66758, 119006, 106672, 260649],
        [130728, 128070, 101252, 123018, 128352, 128352, 99048, 123146, 128070, 260649],
        [130728, 82206, 108792, 72094, 84028, 99166, 69442, 97048, 82108, 260649],
        [130728, 124350, 81384, 89720, 91712, 67618, 112848, 69712, 104160, 260649],
        [130728, 83928, 129720, 116966, 97968, 81084, 101252, 127450, 83928, 260649],
        [130728, 124392, 128456, 67960, 121150, 98018, 85240, 82206, 124388, 260649],
        [130728, 126222, 112152, 96008, 120560, 77928, 73160, 96008, 111648, 260649],
        [130728, 82918, 70600, 125702, 78322, 121744, 116762, 103328, 82918, 260649],
        [130728, 74992, 80048, 73296, 129766, 128450, 97072, 116210, 93424, 260649],
        [130728, 93744, 106800, 101784, 73160, 96008, 125116, 126828, 112440, 260649],
        [130728, 127628, 120948, 102632, 120582, 78074, 128532, 85966, 127628, 260649],
    ]

    assert list(encode(TEST_DATA, 6, 2)) == expected


def test_encode_unicode():
    # These two should encode to the same string
    uc = u"love 💔"
    by = b"love \xf0\x9f\x92\x94"

    expected = [
        [130728, 120256, 108592, 115526, 126604, 103616, 66594, 126094, 128318, 260649],
        [130728, 125456, 83916, 107396, 83872, 97968, 77702, 98676, 128352, 260649],
        [130728, 86496, 128114, 90190, 98038, 72124, 72814, 81040, 86256, 260649]]

    assert encode(uc) == expected
    assert encode(by) == expected


def test_force_binary_encode():
    # Test forcing binary encoding for data that would normally use text compaction
    text_data = "ABC123"
    
    # Expected encoding when forced to binary mode
    expected = [
        [130728, 120256, 108592, 101940, 82448, 120908,  70672,  69848, 128318, 260649],
        [130728, 125456, 121288, 97968,  97968,  97968, 124380, 127396, 128352, 260649],
        [130728,  86496, 102974, 71550, 100246, 102182,  95280,  69456, 86256,  260649]
    ]
    
    # Force binary encoding
    assert list(encode(text_data, force_binary=True)) == expected


def test_force_row_height():
    # Test forcing a specific row height
    # short that data will never naturally fill the row height
    test_data = "?"
    row_height = 15
    
    assert len(encode(test_data, force_rows=row_height, columns=6)) == row_height

def test_encode_macro_single_segment():
    # Test macro PDF417 with only one segment
    test_data = "single segment"
    file_id = [123]
    
    # Expected encoding for a single segment macro PDF417
    # TODO: Consider hooking we can compare the high level encoding
    expected = [
       [
        [130728, 125680, 110320, 98892, 121244, 117104, 103616, 69830, 128318, 260649],
        [130728, 129678, 118888, 119184, 100598, 97968, 97968, 97968, 129720, 260649],
        [130728, 86496, 102290, 116714, 106876, 83518, 106686, 100306, 119934, 260649],
        [130728, 89720, 125680, 82440, 118968, 122738, 68996, 102088, 119520, 260649],
        [130728, 120588, 123522, 110492, 72680, 80632, 120672, 108428, 120624, 260649],
       ]
    ]
    
    result = encode_macro(test_data, file_id=file_id)
    assert len(result) == len(expected)
    assert result[0] == expected[0]


def test_encode_macro_multiple_segments():
    # Test macro PDF417 with multiple segments
    file_id = [456]
    
    # First segment
    test_data = b"two segments"
    result = encode_macro(test_data, segment_size=6, file_id=file_id)
    assert len(result) == 2
    expected1 = [
        [130728, 125680, 120440, 69008, 105860, 105524, 103520, 68708, 128318, 260649],
        [130728, 128280, 97968, 97968, 81702, 108422, 108292, 129198, 129720, 260649],
        [130728, 86496, 100306, 120312, 106876, 83838, 71864, 120060, 108792, 260649],
        [130728, 89720, 81384, 67686, 105024, 122562, 124818, 125086, 119520, 260649]
    ]
    assert result[0] == expected1
    expected2 = [
        [130728, 125680, 120440, 67022, 70688, 105240, 100390, 68708, 128318, 260649],
        [130728, 128280, 97968, 81702, 108422, 108290, 129198, 81740, 129720, 260649],
        [130728, 86496, 120312, 106876, 83838, 100308, 71964, 67496, 108792, 260649],
        [130728, 89720, 102552, 100056, 94008, 99976, 121356, 117694, 119520, 260649]
    ]
    assert result[1] == expected2


def test_max_barcode_size():
    # Borderline
    encode("x" * 1853, columns=16, security_level=6)

    # Data too long
    with pytest.raises(ValueError) as ex:
        encode("x" * 1854, columns=16, security_level=6)
    assert str(ex.value) == "Data too long. Generated bar code has length descriptor of 944. Maximum is 928."

    # Too few rows
    with pytest.raises(ValueError) as ex:
        encode("x", columns=16, security_level=1)
    assert str(ex.value) == "Generated bar code has 1 rows. Minimum is 3 rows. Try decreasing column count."

    # Too many rows
    with pytest.raises(ValueError) as ex:
        encode("x" * 1853, columns=8, security_level=6)
    assert str(ex.value) == "Generated bar code has 132 rows. Maximum is 90 rows. Try increasing column count."
