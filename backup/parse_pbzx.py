#!/usr/bin/env python
# https://gist.github.com/Lekensteyn (Peter Wu)
#
# Extract .cpio file from a pbzx Payload file.
#
# Based on https://gist.github.com/pudquick/ac29c8c19432f2d200d4. This version
# adds a command-line interface, improves efficiency (1 MiB chunks instead of a
# full copy in memory), adds Python 3 compatibility and automatically
# decompresses stuff (some blocks may not be compressed).
#
# Example usage (from Python):
#
#   parse_pbzx(open('PayloadJava', 'rb'), open('PayloadJava.cpio', wb'))
#
# Example usage (from shell):
#
#   # These are all equivalent
#   ./parse_pbzx.py < PayloadJava > PayloadJava.cpio
#   ./parse_pbzx.py PayloadJava > PayloadJava.cpio
#   ./parse_pbzx.py PayloadJava PayloadJava.cpio
#
# Another example, extract Payload from a .pkg file, convert it to a cpio.xz
# archive (this script) and list contents (cpio -t):
#
#   bsdtar -xOf some.pkg Payload | ./parse_pbzx.py Payload | cpio -t
#
# Kernel extraction example:
#
#   tar -xOf Essentials.pkg Payload | ./parse_pbzx.py | cpio -idmu ./System/Library/Kernels

from __future__ import print_function

import struct
import sys
from contextlib import contextmanager
import subprocess


def dbg_print(*args):
    # Uncomment next line for debugging
    # print(*args, file=sys.stderr)
    pass


def read_f(f, count):
    """Try to fully read data, raising EOFError on short reads."""
    data = f.read(count)
    read_bytes = len(data)
    if read_bytes != count:
        raise EOFError("Read %d, expected %d" % (read_bytes, count))
    return data


def copy_data(f_in, f_out, count):
    """Copy in chunks of a megabyte to avoid excess memory waste."""
    while count > 0:
        sz = min(count, 1024**2)
        f_out.write(read_f(f_in, sz))
        count -= sz


@contextmanager
def unxz(f_out):
    # proc = subprocess.Popen(["unxz"], stdin=subprocess.PIPE, stdout=f_out)
    proc = subprocess.Popen(["zcat"], stdin=subprocess.PIPE, stdout=f_out)
    try:
        yield proc.stdin
    finally:
        proc.stdin.close()
        ret = proc.wait()
        if ret != 0:
            raise OSError("Decompression failed with status code %d" % ret)


def parse_pbzx(pbzx_file, cpio_file):
    magic = read_f(pbzx_file, 4)
    if magic != b'pbzx':
        raise RuntimeError("Error: Not a pbzx file")
    # Read 8 bytes for initial flags
    flags = read_f(pbzx_file, 8)
    # Interpret the flags as a 64-bit big-endian unsigned int
    flags = struct.unpack('>Q', flags)[0]
    out_offset, in_offset = 0, 4 + 8
    while (flags & (1 << 24)):
        # Read in more flags
        flags = read_f(pbzx_file, 8)
        flags = struct.unpack('>Q', flags)[0]
        # Read in length
        f_length = read_f(pbzx_file, 8)
        f_length = struct.unpack('>Q', f_length)[0]

        if f_length == 0x1000000:
            # Literal copy
            copy_data(pbzx_file, cpio_file, f_length)
        else:
            xzmagic = read_f(pbzx_file, 6)
            dbg_print("Flags: %#018x  Length: %r  Magic: %r" % (flags, f_length, xzmagic))
            if xzmagic != b'\xfd7zXZ\x00':
                cpio_file.close()
                # raise RuntimeError("Error: Header is not xar file header: offset %d, magic %r" % (offset, xzmagic))
                raise RuntimeError("Error: Header is not xar file header: offset %d, magic %r" % (0, xzmagic))
            else:
                with unxz(cpio_file) as unxz_f:
                    unxz_f.write(xzmagic)
                    # Do not copy header magic again (-6)
                    copy_data(pbzx_file, unxz_f, -6 + f_length)

        in_offset += 8 + 8 + f_length
        out_offset += f_length
        dbg_print("Read %d bytes, wrote %d bytes so far" % (in_offset, out_offset))
    try:
        cpio_file.close()
    except:
        pass

if __name__ == '__main__':
    def open_file(argno, mode, f):
        if len(sys.argv) > argno:
            return open(sys.argv[argno], mode)
        # Access binary stdin/stdout in Python 3
        if hasattr(f, "buffer"):
            return f.buffer
        else:
            return f
    in_file = open_file(1, "rb", sys.stdin)
    out_file = open_file(2, "wb", sys.stdout)
    parse_pbzx(in_file, out_file)
