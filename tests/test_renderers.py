from pdf417 import render_svg, render_image, encode
from pdf417.rendering import barcode_size, modules
from PIL.Image import Image
from xml.etree.ElementTree import ElementTree

codes = encode("hello world!")


def test_render_svg():
    scale = 2
    ratio = 4
    description = "hi there"

    tree = render_svg(codes, scale=scale, ratio=ratio, description=description)
    assert type(tree) == ElementTree
    assert tree.findtext("description") == description

    # Test expected size
    width, height = barcode_size(codes)

    root = tree.getroot()

    assert root.get("width") == str(width * scale)
    assert root.get("height") == str(height * scale  * ratio)
    assert root.get("version") == "1.1"
    assert root.get("xmlns") == "http://www.w3.org/2000/svg"

    # Check number of rendered modules (only visible ones)
    expected_module_count = len([v for x, y, v in modules(codes) if v])
    actual_module_count = len(root.findall('g/rect'))

    assert expected_module_count == actual_module_count


def test_render_image():
    width, height = barcode_size(codes)

    image = render_image(codes)
    assert type(image) == Image

    image = render_image(codes, scale=1, ratio=1, padding=0)
    assert (image.width, image.height) == (width, height)

    image = render_image(codes, scale=2, ratio=1, padding=0)
    assert (image.width, image.height) == (2 * width, 2 * height)

    image = render_image(codes, scale=2, ratio=2, padding=0)
    assert (image.width, image.height) == (2 * width, 4 * height)

    image = render_image(codes, scale=2, ratio=2, padding=20)
    assert (image.width, image.height) == (2 * width + 40, 4 * height + 40)

    # Check actual pixels
    fg_color="LemonChiffon"
    bg_color="#aabbcc"

    fg_parsed = (255, 250, 205)
    bg_parsed = (170, 187, 204)

    image = render_image(codes, scale=1, ratio=1, padding=0, fg_color="LemonChiffon", bg_color="#aabbcc")
    px = image.load()

    for column, row, visible in modules(codes):
        expected = fg_parsed if visible else bg_parsed
        assert px[column, row] == expected
