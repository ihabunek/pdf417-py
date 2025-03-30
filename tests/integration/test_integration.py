from pdf417gen import encode, render_image
from tests.integration.testing_utils import encode_large_data, decode_images

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