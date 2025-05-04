import sys
import os
import zlib

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Union
from PIL import Image

from pdf417gen import encode, render_image


def print_usage():
    print("Usage: pdf417gen [command]")
    print("")
    print("Commands:")
    print("  help    show this help message and exit")
    print("  encode  generate a bar code from given input")
    print("")
    print("https://github.com/ihabunek/pdf417gen")


def print_err(msg: str):
    sys.stderr.write('\033[91m' + msg + '\033[0m' + "\n")


def get_parser() -> ArgumentParser:
    # Use the formatter that preserves description formatting
    parser = ArgumentParser(
        usage="%(prog)s encode [options] [text]",
        epilog="https://github.com/ihabunek/pdf417gen",
        description="Generate a PDF417 barcode from given input",
        formatter_class=RawDescriptionHelpFormatter
    )

    parser.add_argument("text", type=str, nargs="?",
                        help="Text or data to encode. Alternatively data can be piped in.")

    parser.add_argument("-c", "--columns", dest="columns", type=int,
                        help="The number of columns (default: 6).",
                        default=6)

    parser.add_argument("-l", "--security-level", dest="security_level", type=int,
                        help="Security level (default: 2).",
                        default=2)

    parser.add_argument("-e", "--encoding", dest="encoding", type=str,
                        help="Character encoding used to decode input (default: utf-8).",
                        default='utf-8')

    parser.add_argument("-s", "--scale", dest="scale", type=int,
                        help="Module width in pixels (default: 3).",
                        default=3)

    parser.add_argument("-r", "--ratio", dest="ratio", type=int,
                        help="Module height to width ratio (default: 3).",
                        default=3)

    parser.add_argument("-p", "--padding", dest="padding", type=int,
                        help="Image padding in pixels (default: 20).",
                        default=20)

    parser.add_argument("-f", "--foreground-color", dest="fg_color", type=str,
                        help="Foreground color in hex (default: #000000).",
                        default="#000000")

    parser.add_argument("-b", "--background-color", dest="bg_color", type=str,
                        help="Background color in hex (default: #FFFFFF).",
                        default="#FFFFFF")

    parser.add_argument("-o", "--output", dest="output", type=str,
                        help="Target file (if not given, will just show the barcode).")

    # Create a group for advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    
    # Add force binary option
    advanced_group.add_argument("--force-binary", dest="force_binary", action="store_true",
                        help="Force byte compaction mode (useful for pre-compressed data).")
                        
    # Add compression option
    advanced_group.add_argument("--compress", dest="compress", action="store_true",
                        help="Precompress data using zlib before encoding (useful for text data).")

    # Create a group for macro options
    macro_group = parser.add_argument_group('Macro PDF417 Options (for large data)')
    
    # Add macro encoding support
    macro_group.add_argument("--macro", dest="use_macro", action="store_true",
                        help="Use Macro PDF417 for large data.")
                        
    macro_group.add_argument("--segment-size", dest="segment_size", type=int,
                        help="Maximum size in bytes for each segment (default: 800).",
                        default=800)
                        
    macro_group.add_argument("--file-name", dest="file_name", type=str,
                        help="Include file name in Macro PDF417 metadata.")

    return parser


def do_encode(raw_args: List[str]):
    args = get_parser().parse_args(raw_args)
    data: Union[str, bytes] = args.text

    # If no text is given, check stdin
    if not data:
        data = sys.stdin.buffer.read()

    if not data:
        print_err("No input given")
        return

    try:
        # Apply compression if requested
        if args.compress:
            if isinstance(data, str):
                data = data.encode(args.encoding)
            data = zlib.compress(data)
            args.force_binary = True  # Force binary mode for compressed data
            
        if args.use_macro:
            # Use macro encoding for large data
            from pdf417gen import encode_macro
            
            codes = encode_macro(
                data,
                columns=args.columns,
                security_level=args.security_level,
                encoding=args.encoding,
                segment_size=args.segment_size,
                file_name=args.file_name,
                force_binary=args.force_binary,
            )
            
            # Handle multiple barcodes
            images = []
            for i, barcode in enumerate(codes):
                image = render_image(
                    barcode,
                    scale=args.scale,
                    ratio=args.ratio,
                    padding=args.padding,
                    fg_color=args.fg_color,
                    bg_color=args.bg_color,
                )
                images.append(image)
                
            if args.output:
                # Save multiple images with suffix
                base_name, ext = os.path.splitext(args.output)
                for i, image in enumerate(images):
                    output_file = f"{base_name}_{i+1:03d}{ext}"
                    image.save(output_file)
                print(f"Saved {len(images)} barcode images with prefix {base_name}_")
            else:
                # Show first image if there are too many
                if len(images) > 5:
                    print(f"Generated {len(images)} barcode images. Showing first one.")
                    images[0].show()
                else:
                    # Concatenate images into one before showing
                    total_width = max(img.width for img in images)
                    total_height = sum(img.height for img in images)
                    combined_image = Image.new('RGB', (total_width, total_height), args.bg_color)
                    
                    y_offset = 0
                    for img in images:
                        combined_image.paste(img, (0, y_offset))
                        y_offset += img.height
                    
                    combined_image.show()
        else:
            # Standard encoding
            codes = encode(
                data,
                columns=args.columns,
                security_level=args.security_level,
                encoding=args.encoding,
                force_binary=args.force_binary
            )

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
    except Exception as e:
        print_err(str(e))
        return


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[2:]
    
    if command == "encode":
        do_encode(args)
    else:
        print_usage()
