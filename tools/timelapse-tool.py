#!/usr/bin/env python3
import sys, os, math, exif
from datetime import datetime
from argparse import ArgumentParser
from cairosvg import svg2png

def gen_clock_img(fname, time, args):
    factor = args.size / 200
    svg = [
        "<?xml version=\"1.0\"?>",
        "<svg height=\"%d\" width=\"%d\" >" % (args.size, args.size),
        "<g style=\"fill-opacity:1.0; stroke:black; stroke-width:1;\">"
    ]

    def radial(a, r):
        arad = math.radians(a)
        return (100 * factor + math.cos(arad) * r, 100 * factor - math.sin(arad) * r)

    def line(start, end, stroke_width):
        svg.append("<line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" style=\"stroke-linecap: round; stroke-width: %spx;\" />" %
            (start[0], start[1], end[0], end[1], stroke_width))

    # dial
    for a in range(0, 359, 30):
        if a % 90 == 0:
            line(radial(a, 60 * factor), radial(a, 94 * factor), 10 * factor)
        else:
            line(radial(a, 70 * factor), radial(a, 94 * factor), 7 * factor)

    # hour hand
    line((100 * factor,100 * factor), radial(90 - (30 * (time.hour - 1) + time.minute / 2 + time.second / 120), 60 * factor), 9 * factor)

    # minute hand
    line((100 * factor,100 * factor), radial(90 - (6 * time.minute + time.second / 10), 85 * factor), 6 * factor)

    svg.append("</g></svg>")
    svg2png(bytestring="".join(svg), write_to=fname + ".png")

def enumerate_photos(input_path, field):
    files = {}
    with os.scandir(input_path) as it:
        for fname in it:
            if not fname.is_file():
                continue
            with open(fname, "rb") as f:
                img = exif.Image(f)
                date = datetime.strptime(getattr(img, field), exif.DATETIME_STR_FORMAT)
            files[date] = fname

    return files

def cmd_number_photos(args):
    files = enumerate_photos(args.dir, args.field)
    for i, date in enumerate(sorted(files.keys()), start=args.offset):
        fname = files[date]
        os.rename(fname, os.path.join(args.dir, (args.format % i) + os.path.splitext(fname)[1].lower()))

def cmd_clocks_from_photos(args):
    outdir = args.outdir or os.path.join(args.input, "clocks")
    files = enumerate_photos(args.input, args.field)

    os.makedirs(outdir, exist_ok=True)
    for date, fname in files.items():
        sys.stdout.write(fname.name + "\r")
        sys.stdout.flush()
        gen_clock_img(os.path.join(outdir, os.path.splitext(os.path.basename(fname))[0]), date, args)

if __name__ == "__main__":
    parser = ArgumentParser(description="Utility functions for producting timelapse videos with AVISynth")
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("number-photos", help="Sort a directory full of photos by EXIF time and rename them into consecutive increasing numbers")
    sub.add_argument("dir", help="The directory containing the photos")
    sub.add_argument("--format", default="%04d", help="String format to generate the file name, defaults to a four-digit decimal number")
    sub.add_argument("--offset", default=0, type=int, help="Starting index, defaults to 0")
    sub.add_argument("--field", default="datetime_original", help="EXIF field to sort by, defaults to datetime_original")
    sub.set_defaults(func=cmd_number_photos)

    sub = subparsers.add_parser("clocks-from-photos", help="Generate clock images from a set of photos. The clock images will be named like the corresponding photos, with the extension replaced by .png")
    sub.add_argument("input", help="The directory containing the photos")
    sub.add_argument("-o", "--outdir", default="", help="The directory receiving the generated clock images. Defaults to a subdirectory 'clocks' inside the image directory. Will be created if it does not exist.")
    sub.add_argument("--size", default=500, help="Size of the rectangular clock image in pixels. Defaults to 500.")
    sub.add_argument("--field", default="datetime_original", help="EXIF field to sort by, defaults to datetime_original")
    sub.set_defaults(func=cmd_clocks_from_photos)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    args.func(args)
