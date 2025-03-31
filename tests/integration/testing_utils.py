from PIL import Image
from pdf417decoder import PDF417Decoder # type: ignore
from pdf417gen import encode_macro
import pdf417gen.rendering
from typing import List, Union

# add-hoc untility to decode a list of images and reassamble the encoded data
def decode_images(images: List[Image.Image]) -> bytearray:
    info_list = []
    for image in images:
        decoder = PDF417Decoder(image)
        if not decoder.decode():
            raise ValueError('Failed to decode image')
        info_list.extend(decoder.barcodes_info) # type: ignore
    return PDF417Decoder.assemble_data(info_list) # type: ignore

def encode_large_data(data: Union[str, bytes], columns: int = 10, scale: int = 3, force_binary: bool = False) -> List[Image.Image]:
    """
    Encode large data using Macro PDF417 and return a list of PIL Images.
    
    Args:
        data: String or bytes data to encode
        columns: Number of columns (1-30)
        scale: Scale factor for the barcode images
        force_binary: Force byte compaction mode (useful for pre-compressed data)
        
    Returns:
        List of PIL Image objects containing the encoded barcodes
    """
    barcodes = encode_macro(data, columns=columns, file_name = "foobar", force_binary=force_binary)
    return [pdf417gen.rendering.render_image(barcode, scale=scale) for barcode in barcodes]
