import logging
import sys

from argparse import ArgumentParser

from pdf417.encoding import encode
from pdf417.rendering import render_image, render_svg


def encode_data(args):
    if not args.text:
        logging.info("Waiting data on stdin.")
        args.text = sys.stdin.read()

    codes = encode(
        args.text,
        columns=args.columns,
        security_level=args.security_level,
        encoding=args.encoding,
        numeric_compaction=args.numeric_compaction,
    )

    if args.kind=='svg':
        xml = render_svg(
            codes,
            scale=args.scale,
            ratio=args.ratio,
            padding=args.padding,
            fg_color=args.fg_color,
            bg_color=args.bg_color,
        )
        import xml.etree.ElementTree as ET
        print(ET.tostring(xml.getroot()))
    else:
        image = render_image(
            codes,
            scale=args.scale,
            ratio=args.ratio,
            padding=args.padding,
            fg_color=args.fg_color,
            bg_color=args.bg_color,
        )

        if args.output:
            image.save(args.output)
        else:
            image.show()


parser = ArgumentParser(epilog="https://github.com/mosquito/pdf417",
                        description="Generate a bar code from given input")

parser.set_defaults(func=lambda *_: parser.print_help())


subparsers = parser.add_subparsers(help="Encodes text to barcode")
subparser = subparsers.add_parser("encode")

subparser.add_argument("text", type=str, nargs="?",
                       help="Text or data to encode. "
                            "Alternatively data can be piped in.")

subparser.add_argument("-c", "--columns", type=int, default=6,
                       help="The number of columns (default is 6).")

subparser.add_argument("-l", "--security-level", default=2, type=int,
                       help="Security level (default is 2).")

subparser.add_argument("-e", "--encoding", type=str, default='utf-8',
                       help="Character encoding used to decode "
                            "input (default is utf-8).")

subparser.add_argument("-n", "--numeric_compaction", action='store_true',
                       help="This mode can pack almost 3 digits "
                            "(2.93) info a symbol character")

subparser.add_argument("-s", "--scale", default=3, type=int,
                       help="Module width in pixels (default is 3).")

subparser.add_argument("-r", "--ratio", dest="ratio", type=int, default=3,
                       help="Module height to width ratio (default is 3).")

subparser.add_argument("-p", "--padding", default=20, type=int,
                       help="Image padding in pixels (default is 20).")

subparser.add_argument("-f", "--foreground-color", dest="fg_color", type=str,
                       help="Foreground color in hex (default is '#000000').",
                       default="#000000")

subparser.add_argument("-b", "--background-color", dest="bg_color", type=str,
                       help="Foreground color in hex (default is '#FFFFFF'.",
                       default="#FFFFFF")

subparser.add_argument("-o", "--output", dest="output", type=str,
                       help="Target file (if not given, "
                            "will just show the barcode).")
subparser.add_argument("-k", "--kind", type=str, default='image',
                       help=" what kind of image to produce eg image|svg "
                            "input (default is image).")
subparser.set_defaults(func=encode_data)


def entrypoint():
    logging.basicConfig(
        format='\033[91m%(message)s\033[0m',
        level=logging.INFO
    )

    arguments = parser.parse_args()
    try:
        arguments.func(arguments)
    except Exception as e:
        logging.exception("%r", e)
        return 10

    return 0


def main():
    exit(entrypoint())


if __name__ == '__main__':
    main()
