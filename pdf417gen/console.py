import os
import sys

from datetime import datetime
from optparse import OptionParser

from pdf417gen import encode, render_image, render_svg


def print_usage():
    print("Usage: pdf417gen [command]")
    print("")
    print("https://github.com/ihabunek/pdf417gen")
    print("")
    print("commands:")
    print("  help    show this help message and exit")
    print("  encode  generate a bar code from given input")


def print_err(msg):
    sys.stderr.write('\033[91m' + msg + '\033[0m' + "\n")


def do_encode():
    usage = (
        "pdf417gen encode [options] TEXT\n"
        "   or: pdf417gen encode [options] < TEXT\n\n"
        "https://github.com/ihabunek/pdf417gen"
    )

    parser = OptionParser(usage=usage)

    parser.add_option("-c", "--columns", dest="columns", type="int",
                      help="The number of columns (default is 6).",
                      default=6)

    parser.add_option("-l", "--security-level", dest="security_level", type="int",
                      help="Security level (default is 2).",
                      default=2)

    parser.add_option("-e", "--encoding", dest="encoding", type="string",
                      help="Character encoding used to decode input (default is utf-8).",
                      default='utf-8')

    parser.add_option("-s", "--scale", dest="scale", type="int",
                      help="Module width in pixels (default is 3).",
                      default=3)

    parser.add_option("-r", "--ratio", dest="ratio", type="int",
                      help="Module height to width ratio (default is 3).",
                      default=3)

    parser.add_option("-p", "--padding", dest="padding", type="int",
                      help="Image padding in pixels (default is 20).",
                      default=20)

    parser.add_option("-f", "--foreground-color", dest="fg_color", type="string",
                      help="Foreground color in hex (default is '#000000').",
                      default="#000000")

    parser.add_option("-b", "--background-color", dest="bg_color", type="string",
                      help="Foreground color in hex (default is '#FFFFFF'.",
                      default="#FFFFFF")

    parser.add_option("-o", "--output", dest="output", type="string",
                      help="Target file (if not given, will just show the barcode).")

    (options, args) = parser.parse_args()

    if not sys.stdin.isatty():
        text = sys.stdin.read()
    elif len(args) > 1:
        text = args[1]
    else:
        print_err("No input given")
        return

    codes = encode(
        text,
        columns=options.columns,
        security_level=options.security_level,
        encoding=options.encoding,
    )

    image = render_image(
        codes,
        scale=options.scale,
        ratio=options.ratio,
        padding=options.padding,
        fg_color=options.fg_color,
        bg_color=options.bg_color,
    )

    if options.output:
        image.save(options.output)
    else:
        image.show()


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None

    if command == 'encode':
        do_encode()
    else:
        print_usage()
