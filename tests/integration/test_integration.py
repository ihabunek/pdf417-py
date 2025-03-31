import zlib
import os
import pytest
from pdf417gen import encode, render_image
try:
    from .testing_utils import encode_large_data, decode_images
except ImportError:
    # these tests will be skipped if pdf417decoder is not installed
    pass

def test_encode_and_decode_short_string():
    # Setup
    test_data = "Hello, PDF417!"
    
    # Encode the data to PDF417 barcode
    codes = encode(test_data, columns=3)
    image = render_image(codes)  # Returns a PIL Image
    
    # Use the decode_images utility to decode the image
    result = decode_images([image])
    
    # Assert the decoded data matches the original data
    assert result.decode('utf-8') == test_data

# Needs the dev branch of the pdf417decoder package
# e.g. https://github.com/sparkfish/pdf417decoder.git#subdirectory=python
def test_encode_and_decode_large_data():
    # Setup
    test_data = b"Large data " * 1000  # Large data to encode
    
    # Encode the data to PDF417 barcode
    images = encode_large_data(test_data)
    
    # Use the decode_images utility to decode the images
    result = decode_images(images)
    
    # Assert the decoded data matches the original data
    assert result == test_data

# Needs the dev branch of the pdf417decoder package
# e.g. https://github.com/sparkfish/pdf417decoder.git#subdirectory=python
def test_encode_and_decode_binary_data_with_forced_binary():
    """Test encoding/decoding binary data with force_binary option enabled."""
    # Create some compressed binary data
    original_data = b"This is some test data that will be compressed " * 50
    compressed_data = zlib.compress(original_data)
    
    # Encode with force_binary=True to preserve binary data structure
    images = encode_large_data(compressed_data, force_binary=True)
    
    # Decode the images
    result = decode_images(images)
    
    # Decompress and verify
    decompressed = zlib.decompress(result)
    assert decompressed == original_data

# Add another test with random binary data
@pytest.mark.parametrize("size", [100, 5000])
def test_encode_and_decode_random_binary(size: int):
    """Test encoding/decoding random binary data with force_binary option."""
    # Generate random binary data
    random_data = os.urandom(size)
    
    # Encode with force_binary=True
    images = encode_large_data(random_data, force_binary=True)
    
    # Decode and verify
    result = decode_images(images)
    assert result == random_data