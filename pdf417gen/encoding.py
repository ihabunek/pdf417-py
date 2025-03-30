import math
import time
from typing import List, Tuple, Union, Optional, Dict, Any

from pdf417gen.codes import map_code_word
from pdf417gen.compaction import compact
from pdf417gen.compaction.numeric import compact_numbers
from pdf417gen.error_correction import compute_error_correction_code_words
from pdf417gen.types import Barcode, Codeword
from pdf417gen.util import chunks, to_bytes

START_CHARACTER = 0x1fea8
STOP_CHARACTER = 0x3fa29
PADDING_CODE_WORD: Codeword = 900

# Maximum nubmer of code words which can be contained in a bar code, including
# the length descriptor, data, error correction and padding
MAX_CODE_WORDS = 928

# Limits on the number of rows and columns which can be contained in a bar code
MIN_ROWS = 3
MAX_ROWS = 90

# Macro PDF417 control block markers
MACRO_MARKER: Codeword = 928
MACRO_TERMINATOR: Codeword = 922
MACRO_OPTIONAL_FIELD_MARKER: Codeword = 923

# Macro PDF417 optional field designators
MACRO_FILE_NAME: Codeword = 0
MACRO_SEGMENT_COUNT: Codeword = 1
MACRO_TIME_STAMP: Codeword = 2
MACRO_SENDER: Codeword = 3
MACRO_ADDRESSEE: Codeword = 4
MACRO_FILE_SIZE: Codeword = 5
MACRO_CHECKSUM: Codeword = 6


def encode(
    data: Union[str, bytes],
    columns: int = 6,
    security_level: int = 2,
    encoding: str = "utf-8"
) -> Barcode:
    if columns < 1 or columns > 30:
        raise ValueError("'columns' must be between 1 and 30. Given: %r" % columns)

    if security_level < 0 or security_level > 8:
        raise ValueError("'security_level' must be between 1 and 8. Given: %r" % security_level)

    num_cols = columns  # Nomenclature

    # Prepare input
    data_bytes = to_bytes(data, encoding)

    # Convert data to code words and split into rows
    code_words = encode_high(data_bytes, num_cols, security_level)
    rows = list(chunks(code_words, num_cols))

    return list(encode_rows(rows, num_cols, security_level))


def encode_rows(rows: List[Tuple[Codeword, ...]], num_cols: int, security_level: int):
    num_rows = len(rows)

    for row_no, row_data in enumerate(rows):
        left = get_left_code_word(row_no, num_rows, num_cols, security_level)
        right = get_right_code_word(row_no, num_rows, num_cols, security_level)

        yield encode_row(row_no, row_data, left, right)


def encode_row(row_no: int, row_words: Tuple[Codeword, ...], left: Codeword, right: Codeword):
    table_idx = row_no % 3

    # Convert high level code words to low level code words
    left_low = map_code_word(table_idx, left)
    right_low = map_code_word(table_idx, right)
    row_words_low = [map_code_word(table_idx, word) for word in row_words]

    return [START_CHARACTER, left_low] + row_words_low + [right_low, STOP_CHARACTER]


def encode_high(data: bytes, columns: int, security_level: int) -> List[Codeword]:
    """Converts the input string to high level code words.

    Including the length indicator and the error correction words, but without
    padding.
    """

    # Encode data to code words
    data_words = list(compact(data))
    data_count = len(data_words)

    # Get the padding to align data to column count
    ec_count = 2 ** (security_level + 1)
    padding_words = get_padding(data_count, ec_count, columns)
    padding_count = len(padding_words)

    # Length descriptor includes the data CWs, padding CWs and the descriptor
    # itself but not the error correction CWs
    length_descriptor = data_count + padding_count + 1

    # Total number of code words and number of rows
    cw_count = data_count + ec_count + padding_count + 1
    row_count = math.ceil(cw_count / columns)

    # Check the generated bar code's size is within specification parameters
    validate_barcode_size(length_descriptor, row_count)

    # Join encoded data with the length specifier and padding
    extendend_words = [length_descriptor] + data_words + padding_words

    # Calculate error correction words
    ec_words = compute_error_correction_code_words(extendend_words, security_level)

    return extendend_words + ec_words


def validate_barcode_size(length_descriptor: int, row_count: int):
    if length_descriptor > MAX_CODE_WORDS:
        raise ValueError(
            "Data too long. Generated bar code has length descriptor of %d. "
            "Maximum is %d." % (length_descriptor, MAX_CODE_WORDS))

    if row_count < MIN_ROWS:
        raise ValueError(
            "Generated bar code has %d rows. Minimum is %d rows. "
            "Try decreasing column count." % (row_count, MIN_ROWS))

    if row_count > MAX_ROWS:
        raise ValueError(
            "Generated bar code has %d rows. Maximum is %d rows. "
            "Try increasing column count." % (row_count, MAX_ROWS))


def get_left_code_word(row_no: int, num_rows: int, num_cols: int, security_level: int) -> Codeword:
    table_id = row_no % 3

    if table_id == 0:
        x = (num_rows - 1) // 3
    elif table_id == 1:
        x = security_level * 3 + (num_rows - 1) % 3
    elif table_id == 2:
        x = num_cols - 1
    else:
        raise ValueError("Invalid table_id")

    return 30 * (row_no // 3) + x


def get_right_code_word(row_no: int, num_rows: int, num_cols: int, security_level: int) -> Codeword:
    table_id = row_no % 3

    if table_id == 0:
        x = num_cols - 1
    elif table_id == 1:
        x = (num_rows - 1) // 3
    elif table_id == 2:
        x = security_level * 3 + (num_rows - 1) % 3
    else:
        raise ValueError("Invalid table_id")

    return 30 * (row_no // 3) + x


def get_padding(data_count: int, ec_count: int, num_cols: int) -> List[Codeword]:
    # Total number of data words and error correction words, additionally
    # reserve 1 code word for the length descriptor
    total_count = data_count + ec_count + 1
    mod = total_count % num_cols

    return [PADDING_CODE_WORD] * (num_cols - mod) if mod > 0 else []


def encode_macro(
    data: Union[str, bytes],
    columns: int = 6,
    security_level: int = 2, 
    encoding: str = "utf-8",
    segment_size: int = 800,
    file_id: Optional[List[Codeword]] = None,
    optional_fields: Optional[Dict[int, Any]] = None
) -> List[Barcode]:
    """
    Encode data using Macro PDF417 for large data that needs to be split across
    multiple barcodes.
    
    Args:
        data: The data to encode
        columns: Number of columns in each symbol (1-30)
        security_level: Error correction level (0-8)
        encoding: Character encoding for the data
        segment_size: Maximum size in bytes for each segment
        file_id: Custom file ID codewords or None for auto-generated
        optional_fields: Dictionary of optional fields to include
            {MACRO_FILE_NAME: "filename.txt", 
             MACRO_SEGMENT_COUNT: True,
             MACRO_TIME_STAMP: True or Unix timestamp, 
             MACRO_SENDER: "Sender Name",
             MACRO_ADDRESSEE: "Recipient Name", 
             MACRO_FILE_SIZE: True,
             MACRO_CHECKSUM: True}
    
    Returns:
        List of PDF417 barcodes, each represented as a list of rows
    """
    if columns < 1 or columns > 30:
        raise ValueError("'columns' must be between 1 and 30. Given: %r" % columns)
    
    if security_level < 0 or security_level > 8:
        raise ValueError("'security_level' must be between 0 and 8. Given: %r" % security_level)
    
    # Initialize optional_fields if None
    if optional_fields is None:
        optional_fields = {}

    # Prepare input data as bytes
    data_bytes = to_bytes(data, encoding)
    data_size = len(data_bytes)
    
    # Auto-generate file ID if not provided
    if file_id is None:
        file_id = [int(time.time()) % 900]
    
    # Calculate how many segments we need
    segments: List[bytes] = []
    for i in range(0, data_size, segment_size):
        segments.append(data_bytes[i:i+segment_size])
    
    segment_count = len(segments)
    
    # If segment count is requested, add it to all symbols
    include_segment_count = optional_fields.get(MACRO_SEGMENT_COUNT, False)
    if include_segment_count:
        optional_fields[MACRO_SEGMENT_COUNT] = segment_count
    
    # If file size is requested, add it
    if optional_fields.get(MACRO_FILE_SIZE, False) is True:
        optional_fields[MACRO_FILE_SIZE] = data_size
    
    # If timestamp is requested as boolean, use current time
    if optional_fields.get(MACRO_TIME_STAMP, False) is True:
        optional_fields[MACRO_TIME_STAMP] = int(time.time())
    
    # Generate barcodes for each segment
    barcodes : List[List[List[int]]]= []
    for i, segment_data in enumerate(segments):
        # Determine if this is the last segment
        is_last = (i == segment_count - 1)
        
        # Create control block for this segment
        control_block = create_macro_control_block(
            segment_index=i,
            file_id=file_id,
            optional_fields=optional_fields,
            is_last=is_last
        )
        
        # Encode segment with control block
        barcode = encode_with_control_block(
            segment_data, 
            control_block, 
            columns, 
            security_level, 
            encoding
        )
        
        barcodes.append(barcode)
    
    return barcodes

def create_macro_control_block(
    segment_index: int,
    file_id: List[Codeword],
    optional_fields: Dict[int, Any] = {},
    is_last: bool = False
) -> List[Codeword]:
    """
    Create a Macro PDF417 control block.
    
    Args:
        segment_index: Index of this segment (0-99998)
        file_id: List of codewords for file ID
        optional_fields: Optional fields to include
        is_last: Whether this is the last segment
    
    Returns:
        List of codewords for the control block
    """
    if segment_index < 0 or segment_index > 99998:
        raise ValueError(f"Segment index must be between 0 and 99998. Given: {segment_index}")
    
    control_block = [MACRO_MARKER]
    
    # Add segment index (padded to 5 digits and numeric-compacted)
    segment_index_str = f"{segment_index:05d}"
    numeric_compacted = compact_numbers(to_bytes(segment_index_str))
    control_block.extend(numeric_compacted)
    
    # Add file ID
    control_block.extend(file_id)
    
    # Add optional fields if provided
    if optional_fields:
        for field_id, value in optional_fields.items():
            if field_id not in range(7):  # Valid field designators are 0-6
                raise ValueError(f"Invalid field ID: {field_id}. Must be between 0 and 6.")
                
            field_codewords = encode_optional_field(field_id, value)
            if field_codewords:
                control_block.extend(field_codewords)
    
    # Add terminator for last segment
    if is_last:
        control_block.append(MACRO_TERMINATOR)
    
    return control_block

def encode_optional_field(field_id: int, value: Any) -> List[Codeword]:
    """
    Encode an optional field for the control block.
    
    Args:
        field_id: Field designator (0-6)
        value: Field value to encode
    
    Returns:
        List of codewords for the optional field or empty list if invalid
    """
    result : List[Codeword] = [MACRO_OPTIONAL_FIELD_MARKER, field_id]
    
    if field_id == MACRO_SEGMENT_COUNT:
        # Segment count (numeric compaction, 5 digits max)
        count_str = f"{value:05d}"
        result.extend(compact_numbers(to_bytes(count_str)))
    
    elif field_id == MACRO_TIME_STAMP:
        # Timestamp allows for four code words for the timestamp
        # however these can only represent epoch 900^4 which was
        # apparently "far in the future" when the standard was written
        # but was actually back in 1991
        raise ValueError("Timestamp field is not supported")
    
    elif field_id in (MACRO_FILE_NAME, MACRO_SENDER, MACRO_ADDRESSEE):
        # Text fields use text compaction
        text_value = str(value)
        compacted = list(compact(to_bytes(text_value)))
        result.extend(compacted)
    
    elif field_id == MACRO_FILE_SIZE:
        # File size (numeric)
        file_size = int(value)
        compacted = list(compact_numbers(to_bytes(str(file_size))))
        result.extend(compacted)
    
    elif field_id == MACRO_CHECKSUM:
        # Checksum (CRC-16 CCITT)
        checksum = int(value)
        if checksum < 0 or checksum > 65535:
            raise ValueError("Checksum must be between 0 and 65535")
        # encode as five digits so we always get two code words
        checksum_digits = f"{value:05d}"
        if isinstance(value, int):
            checksum = value
        compacted = list(compact_numbers(to_bytes(checksum_digits)))
        result.extend(compacted)
    
    else:
        return []
    
    return result

def encode_with_control_block(
    data: bytes,
    control_block: List[Codeword],
    columns: int,
    security_level: int,
    encoding: str
) -> Barcode:
    """
    Encode data with a control block.
    
    Args:
        data: Data bytes to encode
        control_block: Control block codewords
        columns: Number of columns
        security_level: Error correction level
        encoding: Character encoding
    
    Returns:
        Encoded PDF417 barcode
    """
    # Compact the data
    data_words = list(compact(data))
    
    # Add control block
    combined_words = data_words + control_block
    
    # Get the padding to align data to column count
    ec_count = 2 ** (security_level + 1)
    padding_words = get_padding(len(combined_words), ec_count, columns)
    
    # Length descriptor includes the data CWs, control block, padding CWs and the descriptor itself
    # but not the error correction CWs
    length_descriptor = len(combined_words) + len(padding_words) + 1
    
    # Total number of code words and number of rows
    cw_count = length_descriptor + ec_count
    row_count = math.ceil(cw_count / columns)
    
    # Check the generated bar code's size is within specification parameters
    validate_barcode_size(length_descriptor, row_count)
    
    # Join all components
    complete_words = [length_descriptor] + combined_words + padding_words
    
    # Calculate error correction words
    ec_words = compute_error_correction_code_words(complete_words, security_level)
    
    # Final codewords
    final_words = complete_words + ec_words
    
    # Split into rows and encode
    rows = list(chunks(final_words, columns))
    return list(encode_rows(rows, columns, security_level))
