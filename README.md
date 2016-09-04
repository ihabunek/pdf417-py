PDF417 barcode generator for Python
===================================

[![Travis](https://img.shields.io/travis/ihabunek/pdf417-py.svg?maxAge=3600&style=flat-square)](https://travis-ci.org/ihabunek/pdf417-py)
[![Author](https://img.shields.io/badge/author-%40ihabunek-blue.svg?maxAge=3600&style=flat-square)](https://twitter.com/ihabunek)
[![License](https://img.shields.io/github/license/ihabunek/pdf417-py.svg?maxAge=3600&style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Package Index](https://img.shields.io/pypi/v/pdf417gen.svg?maxAge=3600&style=flat-square)](https://pypi.python.org/pypi/pdf417gen)

Easily encode your data into a 2D barcode using the PDF417 format.

Licensed under the MIT License, see [LICENSE.md](LICENSE.md).

## Installation

Install using pip:

```
pip install pdf417gen
```

## Usage

Creating bar codes is done in two steps:

* Encode a string to a list of code words using `encode()`
* Render the barcode using one of the rendering functions: `render_image()`,
  `render_svg()`.

Usage overview:

```py
from pdf417gen import encode, render_image, render_svg

# Some data to encode
text = """Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated."""

# Convert to code words
codes = encode(text)

# Generate barcode as image
image = render_image(codes)  # Pillow Image object
image.save('barcode.jpg')

# Generate barcode as SVG
svg = render_svg(codes)  # ElementTree object
svg.write("barcode.svg")
```

## Encoding data

The first step is to encode your data to a list of code words.

`encode(data, columns=6, security_level=2˙)`

### Columns

The bar code size can be customized by defining the number of columns used to
render the data, between 1 and 30, the default value is 6. A bar code can have a
maximum of 90 rows, so for larger data sets you may need to increase the number
of columns to decrease the rows count.

```py
codes = encode(text, columns=12)
image = render_image(codes)
image.show()
```

![Defining column count](images/2_columns.jpg)

### Security level

Increasing the security level will produce stronger (and more numerous) error
correction codes, making the bar code larger, but less prone to corruption. The
security level can range from 0 to 8, and procuces `2^(level+1)` error
correction code words, meaning level 0 produces 2 code words and level 8
produces 512. The default security level is 2.

```py
codes = encode(text, columns=12, security_level=6)
image = render_image(codes)
image.show()
```

![Defining security level](images/3_security_level.jpg)

## Render image

The `render_image` function takes the following options:

* `scale` - module width, in pixels (default: 3)
* `ratio` - module height to width ratio (default: 3)
* `padding` - image padding, in pixels (default: 20)
* `fg_color` - foreground color (default: `#000000`)
* `bg_color` - background color (default: `#FFFFFF`)

\* A module is the smallest element of a barcode, analogous to a pixel. Modules
   in a PDF417 bar code are tall and narrow.

The function returns a
[Pillow Image](pillow.readthedocs.io/en/3.2.x/reference/Image.html) object
containing the barcode.

Colors can be specified as hex codes or using HTML color names.

```py
codes = encode(text, columns=3)
image = render_image(codes, scale=5, ratio=2, padding=5, fg_color="Indigo", bg_color="#ddd")
image.show()
```

![Defining security level](images/4_rendering.jpg)


## Render SVG

The `render_svg` function takes the following options:

* `scale` - module width, in pixels (default: 3)
* `ratio` - module height to width ratio (default: 3)
* `padding` - image padding, in pixels (default: 20)
* `color` - foreground color (default: `#000000`)

The function returns a
[ElementTree](https://docs.python.org/3.5/library/xml.etree.elementtree.html#elementtree-objects)
object containing the barcode in SVG format.

Unlike `render_image`, this function does not take a background color option.
The background is left transparent.

```py
codes = encode(text, columns=3)
svg = render_svg(codes, scale=5, ratio=2, color="Seaweed")
svg.write('barcode.svg')
```

## See also

* [pdf417-php](https://github.com/ihabunek/pdf417-php) - a PHP implementation
* [golang-pdf417](https://github.com/ruudk/golang-pdf417) - a Go implementation
