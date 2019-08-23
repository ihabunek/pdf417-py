from xml.etree.ElementTree import ElementTree, Element, SubElement

try:
    from PIL import Image, ImageColor, ImageOps
except ImportError:
    Image = None
    ImageColor = None
    ImageOps = None


def barcode_size(codes):
    """Returns the barcode size in modules."""
    num_rows = len(codes)
    num_cols = len(codes[0])

    # 17 bodules per column, last column has an additional module
    width = num_cols * 17 + 1
    height = num_rows

    return width, height


def modules(codes):
    """Iterates over barcode codes and yields barcode moudles.

    Yields: column number (int), row number (int), module visibility (bool).
    """

    for row_id, row in enumerate(codes):
        col_id = 0
        for value in row:
            for digit in format(value, 'b'):
                yield col_id, row_id, digit == "1"
                col_id += 1


def parse_color(color):
    assert ImageColor, "Module PIL is not installed"
    return ImageColor.getrgb(color)


def rgb_to_hex(color):
    return '#{0:02x}{1:02x}{2:02x}'.format(*color)


def render_image(codes, scale=3, ratio=3, padding=20, fg_color="#000",
                 bg_color="#FFF"):

    assert Image and ImageOps, "Module PIL is not installed"

    width, height = barcode_size(codes)

    # Translate hex code colors to RGB tuples
    bg_color = parse_color(bg_color)
    fg_color = parse_color(fg_color)

    # Construct the image
    image = Image.new("RGB", (width, height), bg_color)

    # Draw the pixle grid
    px = image.load()
    for x, y, visible in modules(codes):
        px[x, y] = fg_color if visible else bg_color

    # Scale and add padding
    image = image.resize((scale * width, scale * height * ratio))
    image = ImageOps.expand(image, padding, bg_color)

    return image


def render_svg(codes, scale=3, ratio=3, padding=20, fg_color="#000", bg_color=None, description=None):
    # Barcode size in modules
    width, height = barcode_size(codes)
    padding = max(padding,0)    #disallow negative padding

    # Size of each module
    scale_x = scale
    scale_y = scale * ratio

    fg_color = rgb_to_hex(parse_color(fg_color))

    w = str(width * scale_x+2*padding)
    h = str(height * scale_y+2*padding)
    root = Element('svg', dict(
        version = "1.1",
        xmlns = "http://www.w3.org/2000/svg",
        width = w,
        height = h,
        ))

    if description:
        description_element = SubElement(root, 'description')
        description_element.text = description

    if bg_color is not None:
        SubElement(root, 'rect', dict(
            x = "0",
            y = "0",
            width = w,
            height = h,
            fill = bg_color,
            ))

    group = SubElement(root, 'g', dict(
        id = "barcode",
        fill = fg_color,
        stroke = "none",
        transform="translate(%s,%s)" % (padding,padding),
        ))

    # Generate the barcode modules
    for col_id, row_id, visible in modules(codes):
        x = col_id * scale_x
        y = row_id * scale_y

        if visible:
            SubElement(group, 'rect', dict(
                x = str(x),
                y = str(y),
                width = str(scale_x),
                height = str(scale_y),
                ))

    return ElementTree(element=root)
