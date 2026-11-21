"""Deliver the finished v4 front page to the grader, unchanged.

The picture was drawn beforehand by the offline build script
(build_v4.py) and stored here as entry-v4.png. This program is only a
courier: it reads those bytes, checks them (PNG signature, 1024x1024,
8-bit RGB, at most 1 MiB), and writes them out as entry.png in the
folder the grader reads (MAKEFUN_OUTPUT_DIR, or /output by default).

Standard library only, no network, no randomness, no clock, so two
runs write byte-identical output. On success it prints the byte count
and sha256; on any problem it explains on stderr and exits non-zero.
"""

import hashlib
import os
import sys
from pathlib import Path

SOURCE = "entry-v4.png"
TARGET_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WANT_SIZE = (1024, 1024)
WANT_DEPTH = (8, 2)  # 8-bit samples, RGB colour type


def fail(msg):
    print("entry failed: " + msg, file=sys.stderr)
    return 1


def read_source():
    """Return (bytes, error) for the rendered page beside this file."""
    path = Path(__file__).resolve().parent / SOURCE
    if not path.is_file():
        return None, f"{SOURCE} not found beside main.py ({path})"
    blob = path.read_bytes()
    if len(blob) > MAX_BYTES:
        return None, f"{SOURCE} is {len(blob)} bytes, over the 1 MiB cap"
    if blob[:8] != PNG_MAGIC:
        return None, "not a PNG file (wrong signature)"
    if blob[-8:-4] != b"IEND":
        return None, "PNG looks truncated (missing IEND trailer)"
    width = int.from_bytes(blob[16:20], "big")
    height = int.from_bytes(blob[20:24], "big")
    if (width, height) != WANT_SIZE:
        return None, f"picture is {width}x{height}, expected 1024x1024"
    if (blob[24], blob[25]) != WANT_DEPTH:
        return None, (
            f"picture is depth {blob[24]}, colour type {blob[25]}; "
            "expected 8-bit RGB"
        )
    return blob, None


def run():
    blob, err = read_source()
    if err is not None:
        return fail(err)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = Path(out_dir) / TARGET_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({len(blob)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
