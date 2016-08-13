from PIL import Image, ImageColor, ImageOps


def render_image(rows, scale=3, ratio=3, padding=20, fg_color="#000", bg_color="#FFF"):
    num_rows = len(rows)
    num_cols = len(rows[0])

    # Translate hex code colors to RGB tuples
    bg_color = ImageColor.getrgb(bg_color)
    fg_color = ImageColor.getrgb(fg_color)

    # Calculate image size
    width = num_cols * 17 + 1
    height = num_rows

    # Construct the image
    image = Image.new("RGB", (width, height), bg_color)

    px = image.load()
    for row_id, row in enumerate(rows):
        x = 0

        for col_id, value in enumerate(row):
            binary = format(value, 'b')

            for digit_id, digit in enumerate(binary):
                px[x, row_id] = fg_color if digit == "1" else bg_color
                x += 1

    image = image.resize((scale * width, scale * height * ratio))
    image = ImageOps.expand(image, padding, bg_color)

    return image
