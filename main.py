#!/usr/bin/env python3
"""Entry point for the news-image-20261123 entry.

Copies the pre-rendered front page (entry.png, drawn by render.py from
news.json) to the output directory the harness asks for, then checks the
result is a whole PNG of at most 1024 by 1024 pixels and at most 1 MiB.
No network, no randomness: two runs write identical bytes.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    raise SystemExit("entry rejected: " + message)


def check_png(path):
    with open(path, "rb") as handle:
        blob = handle.read()
    if len(blob) > MAX_BYTES:
        fail("image is %d bytes, over the 1 MiB limit" % len(blob))
    if not blob.startswith(PNG_MAGIC):
        fail("image does not start with the PNG magic bytes")
    if not blob.rstrip().endswith(b"IEND" + b"\xaeB`\x82"):
        fail("image is not a whole PNG: the IEND chunk is missing")
    width, height = struct.unpack(">II", blob[16:24])
    if width > MAX_SIDE or height > MAX_SIDE:
        fail("image is %dx%d, over the 1024x1024 limit" % (width, height))
    return width, height, len(blob)


def run():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(SOURCE):
        fail("entry.png is missing from the repository")
    shutil.copyfile(SOURCE, target)
    width, height, size = check_png(target)
    print("wrote %s (%dx%d, %d bytes)" % (target, width, height, size))


if __name__ == "__main__":
    run()
